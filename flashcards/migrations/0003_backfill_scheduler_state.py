"""Bring cards scheduled by the old algorithm onto the new one.

Three things need correcting for existing rows:

* Ease factors only ever decreased under the old code, so every card that was
  ever missed has drifted towards the 1.3 floor. They are pulled back halfway
  to the default rather than reset, which keeps genuine signal without leaving
  cards stuck at the minimum multiplier forever.
* ``difficulty`` was overwritten by whatever the last answer was. It is now
  derived, so it is recomputed here. Anything currently labelled hard is also
  pinned, because the old "Save to Hard List" button wrote to the same field
  and the two cannot be told apart after the fact — pinning keeps every word
  that is on the learner's hard list today on it tomorrow.
* Due dates were timestamps, so a card graded at 9pm came due at 9pm. They are
  snapped to the start of their study day.
"""

from django.db import migrations

from flashcards import scheduler


def forwards(apps, schema_editor):
    UserWord = apps.get_model("flashcards", "UserWord")

    updated = []
    for card in UserWord.objects.all().iterator():
        card.ease_factor = round((card.ease_factor + scheduler.INITIAL_EASE) / 2, 4)

        if card.difficulty == "hard":
            card.flagged = True
        card.difficulty = _derive_difficulty(card)

        if card.status in scheduler.GRADUATED_STATES and card.interval > 0:
            card.next_review_date = scheduler.due_after(0, now=card.next_review_date)

        updated.append(card)
        if len(updated) >= 500:
            _flush(UserWord, updated)
            updated = []
    _flush(UserWord, updated)


def _derive_difficulty(card):
    """Mirror of UserWord.refresh_difficulty, using only historical counters."""
    retention = (card.times_correct / card.times_reviewed * 100) if card.times_reviewed else 0
    if card.lapses >= 3 or (card.times_reviewed >= 3 and retention < 60):
        return "hard"
    if card.reps >= 3 and card.lapses == 0 and retention >= 90:
        return "easy"
    return "normal"


def _flush(UserWord, cards):
    if cards:
        UserWord.objects.bulk_update(cards, ["ease_factor", "difficulty", "flagged", "next_review_date"])


def backwards(apps, schema_editor):
    # The old values cannot be recovered, and the new ones are valid input to
    # the old code, so unapplying is a no-op rather than a failure.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("flashcards", "0002_review_remove_userword_session_correct_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
