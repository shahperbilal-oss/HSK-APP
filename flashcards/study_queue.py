"""Building and serving the study queue.

The previous flow picked one card per request with a bare ``.first()`` on a
fully deterministic ordering, which meant every session ran in the same order,
unseen words were only ever reached once the backlog was empty and were then
uncapped, and getting to the next card depended on the HTTP referer header.

This builds an explicit queue and parks it in the session instead.
"""

from django.db.models import F
from django.utils import timezone

from . import scheduler
from .models import UserWord, Word

SESSION_KEY = "study_queue"

#: How many cards to line up before rebuilding.
QUEUE_LENGTH = 40
#: Roughly one unseen word per this many reviews, so new material is spread
#: through a session instead of stacked at one end of it.
REVIEWS_PER_NEW_CARD = 4
#: How many other cards to put between a card in learning and its next showing.
LEARNING_GAP = 3
#: Learning steps further out than this are left to a later session rather than
#: waited out.
SESSION_HORIZON_MINUTES = 20


def ensure_user_words(user):
    """Create the missing UserWord rows for a learner.

    Called when building a queue or rendering progress, not on every request:
    it costs two counts plus a bulk insert and almost no view needs it.
    """
    if UserWord.objects.filter(user=user).count() >= Word.objects.count():
        return

    existing = set(UserWord.objects.filter(user=user).values_list("word_id", flat=True))
    missing = [UserWord(user=user, word=word) for word in Word.objects.exclude(id__in=existing)]
    if missing:
        UserWord.objects.bulk_create(missing, ignore_conflicts=True)


def interleave(due, fresh):
    """Mix unseen words through the reviews rather than stacking them."""
    if not fresh:
        return list(due)
    if not due:
        return list(fresh)

    fresh = list(fresh)
    queue = []
    for position, card_id in enumerate(due, start=1):
        queue.append(card_id)
        if fresh and position % REVIEWS_PER_NEW_CARD == 0:
            queue.append(fresh.pop(0))
    queue.extend(fresh)
    return queue


def build(user, profile, level):
    """Return an ordered list of UserWord ids to study."""
    ensure_user_words(user)
    now = timezone.now()

    cards = UserWord.objects.filter(user=user)
    if level:
        cards = cards.filter(word__hsk_level=level)

    # Mastered cards stay in the rotation. They are a long interval, not an
    # exit from the schedule; dropping them guaranteed eventual forgetting.
    due = list(
        cards.filter(next_review_date__lte=now)
        .exclude(status=scheduler.NEW)
        .order_by("next_review_date", "-lapses")
        .values_list("id", flat=True)[:QUEUE_LENGTH]
    )

    allowance = min(profile.new_cards_remaining(), max(0, QUEUE_LENGTH - len(due)))
    fresh = []
    if allowance:
        fresh = list(
            cards.filter(status=scheduler.NEW)
            # Most frequent words first so study time buys the most reading
            # ability; unranked words fall to the end.
            .order_by(F("word__frequency_rank").asc(nulls_last=True), "word_id")
            .values_list("id", flat=True)[:allowance]
        )

    return interleave(due, fresh)


def next_card(request, user, profile, level):
    """Return the card to show now, rebuilding the queue when it runs dry."""
    state = request.session.get(SESSION_KEY)
    if not state or state.get("level") != level:
        state = {"level": level, "ids": build(user, profile, level)}

    card = _head(user, state)
    if card is None:
        # Rebuild once: cards may have come due since the queue was made.
        state = {"level": level, "ids": build(user, profile, level)}
        card = _head(user, state)

    request.session[SESSION_KEY] = state
    return card


def advance(request, card):
    """Drop a graded card from the queue, re-queueing it if it is coming back.

    A card mid-way through its learning steps is due again in a minute or ten,
    so it goes back a few places rather than being dropped and waited for.
    """
    state = request.session.get(SESSION_KEY)
    if not state:
        return

    queued = state.get("ids", [])
    # Cards graded from the hard/easy lists are not part of this queue, so
    # they are not put into it.
    was_queued = card.id in queued
    ids = [card_id for card_id in queued if card_id != card.id]
    if was_queued and _returns_this_session(card):
        ids.insert(min(LEARNING_GAP, len(ids)), card.id)

    state["ids"] = ids
    request.session[SESSION_KEY] = state


def reset(request):
    """Forget the queue, e.g. when the learner switches level."""
    request.session.pop(SESSION_KEY, None)


def _head(user, state):
    """Pop ids until one resolves to a live card, and return it."""
    ids = state.get("ids", [])
    while ids:
        card = UserWord.objects.filter(user=user, id=ids[0]).select_related("word").first()
        if card is not None:
            return card
        ids.pop(0)  # Row went away underneath us.
    return None


def _returns_this_session(card):
    if card.status not in (scheduler.LEARNING, scheduler.RELEARNING):
        return False
    minutes_away = (card.next_review_date - timezone.now()).total_seconds() / 60
    return minutes_away <= SESSION_HORIZON_MINUTES
