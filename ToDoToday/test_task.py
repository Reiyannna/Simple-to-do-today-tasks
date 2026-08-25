from datetime import date, timedelta

from task import Task, process_tasks, DATE_FMT


def d(offset_days):
    return date.today() + timedelta(days=offset_days)


def test_new_task_not_expired_and_not_done():
    t = Task.new("Drink water", 7)
    assert t.done_today is False
    assert t.is_expired() is False
    assert t.days_left() == 7


def test_needs_reset_true_on_new_day():
    t = Task.new("Read", 7)
    t.done_today = True
    t.last_reset_date = (date.today() - timedelta(days=1)).strftime(DATE_FMT)
    assert t.needs_reset() is True
    t.apply_daily_reset()
    assert t.done_today is False
    assert t.last_reset_date == date.today().strftime(DATE_FMT)


def test_needs_reset_false_same_day():
    t = Task.new("Read", 7)
    t.done_today = True
    assert t.needs_reset() is False
    t.apply_daily_reset()
    assert t.done_today is True  # unchanged, same day


def test_is_expired_after_duration():
    t = Task.new("One week challenge", 7)
    t.start_date = (date.today() - timedelta(days=7)).strftime(DATE_FMT)
    assert t.is_expired() is True


def test_is_not_expired_before_duration_ends():
    t = Task.new("One week challenge", 7)
    t.start_date = (date.today() - timedelta(days=6)).strftime(DATE_FMT)
    assert t.is_expired() is False


def test_process_tasks_drops_expired_and_resets_others():
    expired = Task.new("Old habit", 1)
    expired.start_date = (date.today() - timedelta(days=2)).strftime(DATE_FMT)

    active = Task.new("Ongoing habit", 30)
    active.done_today = True
    active.last_reset_date = (date.today() - timedelta(days=1)).strftime(DATE_FMT)

    survivors = process_tasks([expired, active])

    assert len(survivors) == 1
    assert survivors[0].id == active.id
    assert survivors[0].done_today is False


def test_todo_only_duration_one_day():
    t = Task.new("Just today", 1)
    assert t.is_expired(as_of=date.today()) is False
    assert t.is_expired(as_of=date.today() + timedelta(days=1)) is True
