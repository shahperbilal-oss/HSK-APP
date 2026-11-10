"""Tests for the spaced repetition scheduler and the study flow around it.

Each test here pins down a behaviour that the previous algorithm got wrong.
"""

import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from flashcards import scheduler, study_queue
from flashcards.models import Review, UserProfile, UserWord, Word

#: Fuzz would make interval assertions flaky, so tests that check exact
#: intervals pass a generator that never moves them.
NO_FUZZ = random.Random()
NO_FUZZ.randint = lambda low, high: 0


def graduated(interval=10, ease=scheduler.INITIAL_EASE, reps=3, due=None, **kwargs):
    """A card that is past its learning steps and due now."""
    return scheduler.Card(
        status=scheduler.REVIEW,
        ease=ease,
        interval=interval,
        reps=reps,
        due=due or timezone.now(),
        **kwargs,
    )


class EaseFactorTests(TestCase):
    def test_easy_raises_the_ease_factor(self):
        # The old algorithm never raised ease, so every card that was ever
        # missed drifted to the 1.3 floor and stayed there.
        card = graduated(ease=2.0)
        self.assertGreater(scheduler.review(card, scheduler.EASY).ease, 2.0)

    def test_good_leaves_the_ease_factor_alone(self):
        card = graduated(ease=2.0)
        self.assertEqual(scheduler.review(card, scheduler.GOOD).ease, 2.0)

    def test_hard_and_again_lower_the_ease_factor(self):
        card = graduated(ease=2.5)
        self.assertLess(scheduler.review(card, scheduler.HARD).ease, 2.5)
        self.assertLess(scheduler.review(card, scheduler.AGAIN).ease, 2.5)

    def test_the_ease_factor_stays_within_bounds(self):
        floor = graduated(ease=scheduler.MIN_EASE)
        self.assertEqual(scheduler.review(floor, scheduler.AGAIN).ease, scheduler.MIN_EASE)

        ceiling = graduated(ease=scheduler.MAX_EASE)
        self.assertEqual(scheduler.review(ceiling, scheduler.EASY).ease, scheduler.MAX_EASE)

    def test_ease_recovers_after_a_run_of_easy_answers(self):
        card = graduated(ease=scheduler.MIN_EASE)
        for _ in range(10):
            card = scheduler.review(card, scheduler.EASY)
        self.assertGreater(card.ease, scheduler.MIN_EASE + 0.5)


class LearningStepTests(TestCase):
    def test_a_new_card_is_shown_again_within_the_session(self):
        # It used to jump straight to a one day interval on first sight.
        card = scheduler.review(scheduler.Card(), scheduler.GOOD)
        self.assertEqual(card.status, scheduler.LEARNING)
        self.assertLess(card.due - timezone.now(), timedelta(minutes=15))

    def test_a_new_card_graduates_after_working_through_the_steps(self):
        card = scheduler.Card()
        for _ in scheduler.LEARNING_STEPS_MINUTES:
            card = scheduler.review(card, scheduler.GOOD)
        self.assertEqual(card.status, scheduler.REVIEW)
        self.assertEqual(card.interval, scheduler.GRADUATING_INTERVAL_DAYS)

    def test_easy_on_a_new_card_skips_the_remaining_steps(self):
        card = scheduler.review(scheduler.Card(), scheduler.EASY, rng=NO_FUZZ)
        self.assertEqual(card.status, scheduler.REVIEW)
        self.assertEqual(card.interval, scheduler.EASY_GRADUATING_INTERVAL_DAYS)

    def test_again_sends_a_learning_card_back_to_the_first_step(self):
        card = scheduler.review(scheduler.Card(), scheduler.GOOD)
        card = scheduler.review(card, scheduler.AGAIN)
        self.assertEqual(card.step, 0)


class LapseTests(TestCase):
    def test_a_lapse_keeps_part_of_the_earned_interval(self):
        # The old code reset interval to zero, treating a card known for
        # months exactly like one never seen before.
        card = scheduler.review(graduated(interval=100), scheduler.AGAIN)
        self.assertEqual(card.status, scheduler.RELEARNING)
        self.assertEqual(card.interval, 50)

    def test_a_lapse_is_counted(self):
        self.assertEqual(scheduler.review(graduated(), scheduler.AGAIN).lapses, 1)

    def test_relearning_returns_the_card_to_the_reduced_interval(self):
        card = scheduler.review(graduated(interval=100), scheduler.AGAIN)
        for _ in scheduler.RELEARNING_STEPS_MINUTES:
            card = scheduler.review(card, scheduler.GOOD, rng=NO_FUZZ)
        self.assertEqual(card.status, scheduler.REVIEW)
        self.assertEqual(card.interval, 50)


class IntervalTests(TestCase):
    def test_good_multiplies_the_interval_by_the_ease_factor(self):
        card = scheduler.review(graduated(interval=10, ease=2.5), scheduler.GOOD, rng=NO_FUZZ)
        self.assertEqual(card.interval, 25)

    def test_hard_grows_the_interval_gently_rather_than_collapsing_it(self):
        # Hard used to force the interval to a single day, which made it more
        # punishing than forgetting the card outright.
        card = scheduler.review(graduated(interval=100), scheduler.HARD, rng=NO_FUZZ)
        self.assertEqual(card.interval, 120)

    def test_easy_grows_the_interval_faster_than_good(self):
        good = scheduler.review(graduated(), scheduler.GOOD, rng=NO_FUZZ)
        easy = scheduler.review(graduated(), scheduler.EASY, rng=NO_FUZZ)
        self.assertGreater(easy.interval, good.interval)

    def test_a_short_interval_always_moves_forward(self):
        # 1 * 1.3 rounds back to 1, which would strand the card there.
        card = scheduler.review(graduated(interval=1, ease=scheduler.MIN_EASE), scheduler.GOOD, rng=NO_FUZZ)
        self.assertGreater(card.interval, 1)

    def test_a_late_review_earns_a_longer_interval(self):
        now = timezone.now()
        on_time = scheduler.review(graduated(interval=10, due=now), scheduler.GOOD, now=now, rng=NO_FUZZ)
        late = scheduler.review(
            graduated(interval=10, due=now - timedelta(days=20)), scheduler.GOOD, now=now, rng=NO_FUZZ
        )
        self.assertGreater(late.interval, on_time.interval)

    def test_intervals_are_capped(self):
        card = graduated(interval=scheduler.MAXIMUM_INTERVAL_DAYS, ease=scheduler.MAX_EASE)
        self.assertLessEqual(scheduler.review(card, scheduler.EASY).interval, scheduler.MAXIMUM_INTERVAL_DAYS)


class FuzzTests(TestCase):
    def test_long_intervals_are_spread_out(self):
        card = graduated(interval=100)
        seen = {scheduler.review(card, scheduler.GOOD).interval for _ in range(60)}
        self.assertGreater(len(seen), 1, "identical intervals leave reviews piled on one day")

    def test_short_intervals_are_left_exact(self):
        card = graduated(interval=1, ease=2.5)
        seen = {scheduler.review(card, scheduler.GOOD).interval for _ in range(30)}
        self.assertEqual(seen, {2}, "intervals below the fuzz floor should be deterministic")


class DueDateTests(TestCase):
    def test_due_dates_land_at_the_start_of_the_study_day(self):
        # A card graded at 9pm used to come due at 9pm the next day, so an
        # evening session an hour earlier would not show it.
        late_evening = scheduler.day_starts_at(scheduler.study_day()) + timedelta(hours=17)
        card = scheduler.review(graduated(interval=1), scheduler.GOOD, now=late_evening, rng=NO_FUZZ)
        self.assertEqual(timezone.localtime(card.due).hour, scheduler.DAY_CUTOFF_HOUR)

    def test_a_late_night_answer_counts_as_the_previous_day(self):
        after_midnight = scheduler.day_starts_at(scheduler.study_day()) - timedelta(hours=2)
        self.assertEqual(
            scheduler.study_day(after_midnight),
            scheduler.study_day(after_midnight - timedelta(hours=6)),
        )


class MasteryTests(TestCase):
    def test_a_mastered_card_is_still_scheduled(self):
        card = graduated(interval=200, reps=20)
        result = scheduler.review(card, scheduler.GOOD)
        self.assertEqual(result.status, scheduler.MASTERED)
        self.assertIsNotNone(result.due)

    def test_a_mastered_card_can_lapse_back_into_relearning(self):
        card = scheduler.Card(status=scheduler.MASTERED, interval=200, reps=20, due=timezone.now())
        self.assertEqual(scheduler.review(card, scheduler.AGAIN).status, scheduler.RELEARNING)


class RejectedInputTests(TestCase):
    def test_an_unknown_rating_is_rejected(self):
        with self.assertRaises(ValueError):
            scheduler.review(graduated(), 99)


class GradingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="learner")
        self.word = Word.objects.create(hsk_level=1, chinese="爱", pinyin="ài", english="to love")
        self.card = UserWord.objects.create(user=self.user, word=self.word)

    def test_hard_counts_as_a_recall(self):
        # It used to increment times_incorrect, so every accuracy figure in
        # the app was understated.
        self.card.grade(scheduler.HARD)
        self.card.refresh_from_db()
        self.assertEqual(self.card.times_correct, 1)
        self.assertEqual(self.card.times_incorrect, 0)

    def test_again_counts_as_a_miss_and_breaks_the_streak(self):
        self.card.grade(scheduler.GOOD)
        self.card.grade(scheduler.AGAIN)
        self.card.refresh_from_db()
        self.assertEqual(self.card.times_incorrect, 1)
        self.assertEqual(self.card.consecutive_correct, 0)

    def test_consecutive_correct_is_maintained(self):
        # The field existed but nothing ever incremented it.
        for _ in range(3):
            self.card.grade(scheduler.GOOD)
        self.card.refresh_from_db()
        self.assertEqual(self.card.consecutive_correct, 3)

    def test_every_answer_is_logged(self):
        self.card.grade(scheduler.GOOD, duration_ms=1500)
        self.card.grade(scheduler.AGAIN)

        self.assertEqual(Review.objects.count(), 2)
        first = Review.objects.earliest("reviewed_at")
        self.assertEqual(first.rating, scheduler.GOOD)
        self.assertEqual(first.state_before, scheduler.NEW)
        self.assertEqual(first.duration_ms, 1500)

    def test_difficulty_is_derived_rather_than_set_by_the_last_answer(self):
        # One correct answer used to relabel a repeatedly failed word "easy"
        # and drop it off the hard list.
        for _ in range(4):
            self.card.grade(scheduler.GOOD)
        for _ in range(4):
            self.card.grade(scheduler.AGAIN)
            self.card.grade(scheduler.GOOD)

        self.card.refresh_from_db()
        self.assertEqual(self.card.difficulty, "hard")

    def test_a_pin_survives_being_graded(self):
        self.card.flagged = True
        self.card.save()

        self.card.grade(scheduler.EASY)

        self.card.refresh_from_db()
        self.assertTrue(self.card.flagged)

    def test_first_learned_is_recorded_whatever_the_first_answer_was(self):
        # It was only ever set on a correct first answer.
        self.card.grade(scheduler.AGAIN)
        self.card.refresh_from_db()
        self.assertIsNotNone(self.card.first_learned)


class StudyQueueTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="learner")
        self.profile = UserProfile.objects.create(user=self.user)
        for index in range(30):
            Word.objects.create(
                hsk_level=1, chinese=f"字{index}", pinyin=f"zi{index}", english=f"word {index}",
                frequency_rank=index,
            )

    def test_new_cards_are_capped_per_day(self):
        self.profile.new_cards_per_day = 5
        self.profile.save()

        queue = study_queue.build(self.user, self.profile, level=1)

        self.assertEqual(len(queue), 5)

    def test_new_cards_come_in_frequency_order(self):
        self.profile.new_cards_per_day = 3
        self.profile.save()

        queue = study_queue.build(self.user, self.profile, level=1)
        ranks = list(
            UserWord.objects.filter(id__in=queue).values_list("word__frequency_rank", flat=True)
        )

        self.assertEqual(sorted(ranks), [0, 1, 2])

    def test_new_cards_are_mixed_through_the_reviews(self):
        # New words used to wait until the whole review backlog was cleared.
        study_queue.ensure_user_words(self.user)
        due = list(UserWord.objects.filter(user=self.user)[:20])
        for card in due:
            card.status = scheduler.REVIEW
            card.interval = 5
            card.next_review_date = timezone.now() - timedelta(days=1)
            card.save()
        self.profile.new_cards_per_day = 3
        self.profile.save()

        queue = study_queue.build(self.user, self.profile, level=1)
        statuses = [
            UserWord.objects.get(id=card_id).status for card_id in queue
        ]

        self.assertIn(scheduler.NEW, statuses[: len(statuses) // 2])

    def test_mastered_cards_stay_in_the_rotation(self):
        # They used to be excluded outright, guaranteeing they were forgotten.
        study_queue.ensure_user_words(self.user)
        card = UserWord.objects.filter(user=self.user).first()
        card.status = scheduler.MASTERED
        card.interval = 200
        card.next_review_date = timezone.now() - timedelta(days=1)
        card.save()

        self.assertIn(card.id, study_queue.build(self.user, self.profile, level=1))


class ReviewViewTests(TestCase):
    def setUp(self):
        self.word = Word.objects.create(hsk_level=1, chinese="爱", pinyin="ài", english="to love")

    def card(self):
        return UserWord.objects.get(word=self.word)

    def test_grading_requires_a_post(self):
        # These were plain links, so anything that prefetched them graded the
        # learner's deck for them.
        self.client.get(reverse("study_session_level", args=[1]))
        response = self.client.get(reverse("review_action", args=[self.card().id, "good"]))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.card().times_reviewed, 0)

    def test_grading_schedules_the_card_and_returns_to_the_session(self):
        self.client.get(reverse("study_session_level", args=[1]))
        target = reverse("study_session_level", args=[1])

        response = self.client.post(
            reverse("review_action", args=[self.card().id, "good"]), {"return_to": target}
        )

        self.assertRedirects(response, target)
        self.assertEqual(self.card().times_reviewed, 1)

    def test_an_offsite_return_target_is_ignored(self):
        self.client.get(reverse("study_session_level", args=[1]))

        response = self.client.post(
            reverse("review_action", args=[self.card().id, "good"]),
            {"return_to": "https://example.com/phish"},
        )

        self.assertEqual(response["Location"], reverse("study_session_level", args=[1]))

    def test_pinning_does_not_grade_the_card(self):
        self.client.get(reverse("study_session_level", args=[1]))

        self.client.post(reverse("review_action", args=[self.card().id, "flag"]))

        self.assertTrue(self.card().flagged)
        self.assertEqual(self.card().times_reviewed, 0)

    def test_the_new_card_allowance_is_spent_as_words_are_introduced(self):
        self.client.get(reverse("study_session_level", args=[1]))
        self.client.post(reverse("review_action", args=[self.card().id, "good"]))

        profile = UserProfile.objects.get()
        self.assertEqual(profile.new_cards_today, 1)
        self.assertEqual(profile.words_studied_today, 1)

    def test_answering_a_started_card_does_not_spend_the_new_allowance(self):
        self.client.get(reverse("study_session_level", args=[1]))
        for _ in range(3):
            self.client.post(reverse("review_action", args=[self.card().id, "good"]))

        self.assertEqual(UserProfile.objects.get().new_cards_today, 1)

    def test_the_stats_page_renders(self):
        # It referenced an unimported name and raised NameError on every visit.
        self.client.get(reverse("study_session_level", args=[1]))
        self.client.post(reverse("review_action", args=[self.card().id, "good"]))

        self.assertEqual(self.client.get(reverse("stats")).status_code, 200)

    def test_a_card_in_learning_comes_back_in_the_same_session(self):
        self.client.get(reverse("study_session_level", args=[1]))
        self.client.post(reverse("review_action", args=[self.card().id, "again"]))

        response = self.client.get(reverse("study_session_level", args=[1]))

        self.assertEqual(response.context["card"].id, self.card().id)
