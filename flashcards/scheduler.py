"""Spaced repetition scheduling.

The grading rules live here rather than on ``UserWord`` so they can be tested
without a database, and so the whole policy can be replaced (with FSRS, say) by
rewriting one function.

The algorithm is SM-2 plus the refinements that make it usable in practice:

* learning steps, so brand new material is seen more than once before it
  disappears for a day;
* relearning steps after a lapse, keeping half of the interval the card had
  earned instead of resetting it to zero;
* an ease factor that can go *up* again — plain SM-2 that only ever subtracts
  drags every card down to the minimum multiplier over time;
* day-aligned due dates, so a card graded at 9pm is available first thing on
  its due day rather than at 9pm that evening;
* credit for reviews done late, since recalling something a month overdue is
  evidence the interval was too short;
* a little randomness, so cards learned in one sitting do not stay clumped
  together for the rest of time.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
from datetime import datetime, time, timedelta

from django.utils import timezone

# --- Grades -----------------------------------------------------------------

AGAIN, HARD, GOOD, EASY = 1, 2, 3, 4
RATINGS = (AGAIN, HARD, GOOD, EASY)
RATING_NAMES = {AGAIN: "again", HARD: "hard", GOOD: "good", EASY: "easy"}
RATING_BY_NAME = {name: rating for rating, name in RATING_NAMES.items()}
PASSING_RATINGS = (HARD, GOOD, EASY)

# --- Card states ------------------------------------------------------------

NEW = "NEW"
LEARNING = "LEARNING"
REVIEW = "REVIEW"
RELEARNING = "RELEARNING"
MASTERED = "MASTERED"

#: States whose cards are scheduled in days rather than minutes.
GRADUATED_STATES = (REVIEW, MASTERED)

# --- Tuning -----------------------------------------------------------------

#: A fresh card is shown again after a minute, then after ten, before it earns
#: a place in the day-scale schedule.
LEARNING_STEPS_MINUTES = (1, 10)
#: A lapsed card is not new material, so one short step is enough.
RELEARNING_STEPS_MINUTES = (10,)

GRADUATING_INTERVAL_DAYS = 1
EASY_GRADUATING_INTERVAL_DAYS = 4

INITIAL_EASE = 2.5
MIN_EASE = 1.3
MAX_EASE = 3.0

HARD_MULTIPLIER = 1.2
EASY_BONUS = 1.3
#: A lapse keeps this share of the interval the card had earned.
LAPSE_MULTIPLIER = 0.5

MINIMUM_INTERVAL_DAYS = 1
MAXIMUM_INTERVAL_DAYS = 365 * 5

FUZZ_RATIO = 0.05
#: Intervals shorter than this are left alone; fuzzing them buys nothing.
FUZZ_FLOOR_DAYS = 3

#: A card at this interval with this many repetitions behind it is called
#: mastered. That is a label on a long interval, not an exit from the schedule.
MASTERED_INTERVAL_DAYS = 21
MASTERED_REPS = 5

#: The study day rolls over at 4am, so a late night session still counts as the
#: previous day and cards due "tomorrow" are not gated behind midnight.
DAY_CUTOFF_HOUR = 4


# --- Day arithmetic ---------------------------------------------------------


def study_day(moment=None):
    """Return the study day a moment belongs to."""
    moment = moment or timezone.now()
    local = timezone.localtime(moment)
    if local.hour < DAY_CUTOFF_HOUR:
        local -= timedelta(days=1)
    return local.date()


def day_starts_at(day):
    """Return the aware datetime at which a study day begins."""
    naive = datetime.combine(day, time(hour=DAY_CUTOFF_HOUR))
    return timezone.make_aware(naive, timezone.get_current_timezone())


def due_after(interval_days, now=None):
    """Return the due datetime for an interval, aligned to a day boundary."""
    now = now or timezone.now()
    return day_starts_at(study_day(now) + timedelta(days=interval_days))


# --- Card state -------------------------------------------------------------


@dataclass(frozen=True)
class Card:
    """The scheduling state of a single card, independent of the database."""

    status: str = NEW
    step: int = 0
    ease: float = INITIAL_EASE
    interval: int = 0
    reps: int = 0
    lapses: int = 0
    due: datetime | None = None

    @property
    def is_graduated(self):
        return self.status in GRADUATED_STATES


# --- Internals --------------------------------------------------------------


def _adjust_ease(ease, rating):
    """Apply the SM-2 ease update for a grade.

    Ratings map onto SM-2's 0-5 quality scale as Again=2, Hard=3, Good=4,
    Easy=5, which makes Good ease-neutral and Easy the only grade that earns
    ease back.
    """
    quality = rating + 1
    delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    return round(min(MAX_EASE, max(MIN_EASE, ease + delta)), 4)


def _clamp_interval(days):
    return int(max(MINIMUM_INTERVAL_DAYS, min(MAXIMUM_INTERVAL_DAYS, round(days))))


def _fuzz(interval, rng):
    """Spread a due date over a small window so reviews do not pile up."""
    if interval < FUZZ_FLOOR_DAYS:
        return interval
    spread = max(1, round(interval * FUZZ_RATIO))
    return _clamp_interval(interval + rng.randint(-spread, spread))


def _days_overdue(card, now):
    """Whole days between when the card came due and when it was answered."""
    if card.due is None:
        return 0
    return max(0, (study_day(now) - study_day(card.due)).days)


def _label(interval, reps):
    if reps >= MASTERED_REPS and interval >= MASTERED_INTERVAL_DAYS:
        return MASTERED
    return REVIEW


def _graduate(card, interval_days, ease, now, rng):
    """Move a card onto the day-scale schedule."""
    interval = _fuzz(_clamp_interval(interval_days), rng)
    reps = card.reps + 1
    return replace(
        card,
        status=_label(interval, reps),
        step=0,
        ease=ease,
        interval=interval,
        reps=reps,
        due=due_after(interval, now),
    )


def _review_learning(card, rating, now, rng):
    """Grade a card that is still working through its learning steps."""
    steps = LEARNING_STEPS_MINUTES

    if rating == AGAIN:
        return replace(card, status=LEARNING, step=0, due=now + timedelta(minutes=steps[0]))

    if rating == HARD:
        # Repeat the current step rather than advancing past it.
        step = min(card.step, len(steps) - 1)
        return replace(card, status=LEARNING, step=step, due=now + timedelta(minutes=steps[step]))

    if rating == EASY:
        return _graduate(card, EASY_GRADUATING_INTERVAL_DAYS, card.ease, now, rng)

    step = card.step + 1
    if step >= len(steps):
        return _graduate(card, GRADUATING_INTERVAL_DAYS, card.ease, now, rng)
    return replace(card, status=LEARNING, step=step, due=now + timedelta(minutes=steps[step]))


def _review_relearning(card, rating, now, rng):
    """Grade a lapsed card working its way back onto the schedule.

    ``card.interval`` already holds the reduced interval assigned when the card
    lapsed, so passing simply restores it.
    """
    steps = RELEARNING_STEPS_MINUTES

    if rating == AGAIN:
        return replace(card, step=0, due=now + timedelta(minutes=steps[0]))

    if rating == HARD:
        step = min(card.step, len(steps) - 1)
        return replace(card, step=step, due=now + timedelta(minutes=steps[step]))

    if rating == GOOD:
        step = card.step + 1
        if step < len(steps):
            return replace(card, step=step, due=now + timedelta(minutes=steps[step]))

    interval = _fuzz(_clamp_interval(card.interval), rng)
    return replace(
        card,
        status=_label(interval, card.reps),
        step=0,
        interval=interval,
        due=due_after(interval, now),
    )


def _review_graduated(card, rating, now, rng):
    """Grade a card that is already on the day-scale schedule."""
    ease = _adjust_ease(card.ease, rating)

    if rating == AGAIN:
        # A lapse costs the card half its interval and a trip through the
        # relearning steps, not everything it has learned.
        interval = _clamp_interval(card.interval * LAPSE_MULTIPLIER)
        return replace(
            card,
            status=RELEARNING,
            step=0,
            ease=ease,
            interval=interval,
            lapses=card.lapses + 1,
            due=now + timedelta(minutes=RELEARNING_STEPS_MINUTES[0]),
        )

    # Recalling a card that is overdue is evidence the interval was too short,
    # so the wait it survived counts towards the next one.
    overdue = _days_overdue(card, now)
    if rating == HARD:
        interval = card.interval * HARD_MULTIPLIER + overdue * 0.25
    elif rating == GOOD:
        interval = (card.interval + overdue / 2) * ease
    else:
        interval = (card.interval + overdue) * ease * EASY_BONUS

    # Rounding can leave a short interval unchanged (1 * 1.2 rounds back to 1),
    # which would strand the card at that interval forever.
    interval = max(_clamp_interval(interval), card.interval + 1)
    return _graduate(card, interval, ease, now, rng)


# --- Public API -------------------------------------------------------------


def review(card, rating, now=None, rng=None):
    """Return the state ``card`` should take after being graded ``rating``."""
    if rating not in RATINGS:
        raise ValueError(f"unknown rating {rating!r}; expected one of {RATINGS}")

    now = now or timezone.now()
    rng = rng or random

    if card.status in (NEW, LEARNING):
        return _review_learning(card, rating, now, rng)
    if card.status == RELEARNING:
        return _review_relearning(card, rating, now, rng)
    return _review_graduated(card, rating, now, rng)


def next_intervals(card, now=None):
    """Preview the interval each grade would produce, for button labels.

    Returned as ``{rating: description}`` with the delay rendered the way a
    learner reads it — minutes while the card is in learning, days after that.
    """
    now = now or timezone.now()
    # A fixed source of randomness keeps the preview stable across a page load;
    # the fuzz applied at grading time is drawn separately.
    rng = random.Random(0)
    previews = {}
    for rating in RATINGS:
        result = review(card, rating, now=now, rng=rng)
        if result.is_graduated:
            previews[rating] = _describe_days(result.interval)
        else:
            delay = max(1, round((result.due - now).total_seconds() / 60))
            previews[rating] = f"{delay} min"
    return previews


def _describe_days(days):
    if days < 30:
        return f"{days} day" + ("" if days == 1 else "s")
    if days < 365:
        months = days / 30.0
        return f"{months:.1f} mo"
    return f"{days / 365.0:.1f} yr"
