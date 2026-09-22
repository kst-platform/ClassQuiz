# SPDX-FileCopyrightText: 2026 ГБПОУ КСТ
#
# SPDX-License-Identifier: MPL-2.0

"""Разбор тестов в диалекте GIFT, который используется в курсах КСТ.

Диалект и регэкспы блоков перенесены из линтера курсов
(``C:\\Users\\Dmitry\\Projects\\_tools\\kt\\gift.py``), но здесь цель другая:
не найти дефекты файла, а превратить вопросы в ``QuizQuestion`` для
КСТ.Квиз. Правила классификации проверены на реальных файлах курса ОП.02
(``Входной тест``), не выдуманы заранее:

- **ВО** (один верный ответ, `=`/`~`) → ``QuizQuestionType.ABCD``.
- **МВ** (несколько верных, вес `%N%` встроен в текст строки ПОСЛЕ маркера
  `~`, например ``~%50%текст`` — не отдельным маркером, как можно было бы
  подумать) → ``QuizQuestionType.CHECK``, вес > 0 → верный ответ.
- Строки с ``->`` — в реальном GIFT это единственный способ закодировать
  и настоящее соответствие, и то, что в курсах называют «ПД» (расставить
  по порядку): авторы курса кодируют порядок как соответствие пункта
  метке вида «место N» (в GIFT нет отдельного типа вопроса на порядок).
  Отличаем по значению меток:
  - если у ВСЕХ пар правая часть — это число (в оболочке из букв вроде
    «место 5» или голое «5») и вместе числа образуют ровно 1..N без
    пропusков — это **ПД** → ``QuizQuestionType.ORDER``, элементы
    сортируются по числу;
  - иначе это **настоящее СО** (сопоставление разных сущностей,
    не позиций) — в ClassQuiz нет типа вопроса «соответствие», такой
    вопрос **пропускается** с понятной причиной в отчёте импорта, а не
    подгоняется под другой тип вкривь.
- Классический маркер ``#N`` (canonical GIFT order-hack) тоже
  поддержан на случай, если он где-то встретится, хотя в реальных
  файлах курса не замечен ни разу.
"""

from __future__ import annotations

import dataclasses
import re

import bleach

from classquiz.config import ALLOWED_TAGS_FOR_QUIZ
from classquiz.db.models import (
    ABCDQuizAnswer,
    QuizQuestion,
    QuizQuestionType,
    VotingQuizAnswer,
)

BLOCK_RE = re.compile(r"::([^:]+)::(.*?)\{(.*?)\n\}", re.DOTALL)
HEADER_RE = re.compile(r"^::", re.MULTILINE)
OPTION_RE = re.compile(r"^(=|~|#\d+)\s*(.*)$")
WEIGHT_PREFIX_RE = re.compile(r"^%(-?[\d.]+)%\s*(.*)$")
# «место 5», «позиция 5», «шаг 5», голое «5» — метка порядка, а не сущность
POSITION_LABEL_RE = re.compile(r"^\D*(\d+)\D*$")

DEFAULT_COLORS = ["#2F678C", "#8F5B60", "#405A67", "#C82E3E"]


@dataclasses.dataclass
class GiftParseResult:
    questions: list[QuizQuestion]
    # (имя_вопроса, причина) — что пропущено и почему, показывается
    # преподавателю после импорта, чтобы вопросы не терялись молча
    skipped: list[tuple[str, str]]
    # ошибки уровня файла (дисбаланс скобок и т.п.) — импорт всё равно
    # продолжается по тем блокам, что удалось разобрать
    problems: list[str]


@dataclasses.dataclass
class _RawQuestion:
    name: str
    text: str
    body: str


def _clean_answer(text: str) -> str:
    return bleach.clean(text.strip(), tags=[], strip=True)


def _clean_question(text: str) -> str:
    return bleach.clean(text.strip(), tags=ALLOWED_TAGS_FOR_QUIZ, strip=True)


def _split_blocks(text: str) -> tuple[list[_RawQuestion], list[str]]:
    problems: list[str] = []
    questions = [
        _RawQuestion(m.group(1).strip(), m.group(2).strip(), m.group(3)) for m in BLOCK_RE.finditer(text)
    ]
    headers = len(HEADER_RE.findall(text))
    if headers != len(questions):
        problems.append(
            f"разобрано {len(questions)} блоков при {headers} заголовках — "
            f"часть вопросов не распозналась и молча выпала, проверьте файл вручную"
        )
    if text.count("{") != text.count("}"):
        problems.append(f"дисбаланс скобок: {text.count('{')} открывающих, {text.count('}')} закрывающих")
    return questions, problems


def _match_pairs(body: str) -> list[tuple[str, str]]:
    """Строки вида `=текст -> метка` или `~текст -> метка` из тела вопроса."""
    pairs = []
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(?:=|~)\s*(.+?)\s*->\s*(.+)$", line)
        if m:
            pairs.append((m.group(1).strip(), m.group(2).strip()))
    return pairs


def _is_order_disguised_as_matching(pairs: list[tuple[str, str]]) -> list[str] | None:
    """Если все правые части — метки позиций 1..N, вернуть тексты в правильном
    порядке. Иначе None (это настоящее соответствие, не порядок)."""
    if not pairs:
        return None
    numbered: list[tuple[int, str]] = []
    seen_positions: set[int] = set()
    for source_text, label in pairs:
        m = POSITION_LABEL_RE.match(label)
        if not m:
            return None
        pos = int(m.group(1))
        if pos in seen_positions:
            return None
        seen_positions.add(pos)
        numbered.append((pos, source_text))
    if sorted(seen_positions) != list(range(1, len(pairs) + 1)):
        return None
    numbered.sort(key=lambda pair: pair[0])
    return [text for _, text in numbered]


def _options(body: str) -> list[tuple[str, str]]:
    """Строки вида `=текст`, `~текст`, `#N текст` из тела вопроса (без `->`)."""
    out = []
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        m = OPTION_RE.match(line)
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def _convert_question(q: _RawQuestion) -> tuple[QuizQuestion | None, str | None]:
    """Вернуть (вопрос, None) при успехе или (None, причина) при пропуске."""
    question_text = _clean_question(q.text)

    if "->" in q.body:
        pairs = _match_pairs(q.body)
        ordered = _is_order_disguised_as_matching(pairs)
        if ordered is None:
            return None, (
                f"«{q.name}»: вопрос на соответствие (не на порядок) — в КСТ.Квиз нет "
                f"такого типа вопроса, добавьте вручную в редакторе"
            )
        if len(ordered) < 2:
            return None, f"«{q.name}»: меньше двух пунктов после разбора порядка — пропущен"
        answers = [VotingQuizAnswer(answer=_clean_answer(t)) for t in ordered]
        return (
            QuizQuestion(question=question_text, time="30", type=QuizQuestionType.ORDER, answers=answers),
            None,
        )

    if re.search(r"^\s*#\d", q.body, re.MULTILINE):
        opts = _options(q.body)
        numbered = []
        for marker, text in opts:
            m = re.match(r"^#(\d+)$", marker)
            if m:
                numbered.append((int(m.group(1)), text))
        if len(numbered) < 2:
            return None, f"«{q.name}»: меньше двух пронумерованных пунктов — пропущен"
        numbered.sort(key=lambda pair: pair[0])
        answers = [VotingQuizAnswer(answer=_clean_answer(t)) for _, t in numbered]
        return (
            QuizQuestion(question=question_text, time="30", type=QuizQuestionType.ORDER, answers=answers),
            None,
        )

    if "%" in q.body:
        opts = _options(q.body)
        answers = []
        for marker, text in opts:
            if marker != "~":
                continue
            wm = WEIGHT_PREFIX_RE.match(text)
            if wm:
                try:
                    weight = float(wm.group(1))
                except ValueError:
                    weight = 0.0
                clean_text = wm.group(2)
            else:
                weight = 0.0
                clean_text = text
            answers.append(
                ABCDQuizAnswer(right=weight > 0, answer=_clean_answer(clean_text), color=None)
            )
        if len(answers) < 2:
            return None, f"«{q.name}»: меньше двух вариантов — пропущен"
        if not any(a.right for a in answers):
            return None, f"«{q.name}»: ни один вариант не отмечен верным (вес > 0) — пропущен"
        for i, a in enumerate(answers):
            a.color = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
        return (
            QuizQuestion(question=question_text, time="30", type=QuizQuestionType.CHECK, answers=answers),
            None,
        )

    # ВО — один верный ответ
    opts = _options(q.body)
    answers = []
    for marker, text in opts:
        if marker not in ("=", "~"):
            continue
        answers.append(ABCDQuizAnswer(right=marker == "=", answer=_clean_answer(text), color=None))
    if len(answers) < 2:
        return None, f"«{q.name}»: меньше двух вариантов ответа — пропущен"
    right_count = sum(1 for a in answers if a.right)
    if right_count != 1:
        return None, f"«{q.name}»: должен быть ровно один верный ответ, найдено {right_count} — пропущен"
    for i, a in enumerate(answers):
        a.color = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
    return (
        QuizQuestion(question=question_text, time="30", type=QuizQuestionType.ABCD, answers=answers),
        None,
    )


def parse_gift(raw_text: str) -> GiftParseResult:
    questions, problems = _split_blocks(raw_text)
    result_questions: list[QuizQuestion] = []
    skipped: list[tuple[str, str]] = []
    for q in questions:
        question, skip_reason = _convert_question(q)
        if question is not None:
            result_questions.append(question)
        elif skip_reason is not None:
            skipped.append((q.name, skip_reason))
    return GiftParseResult(questions=result_questions, skipped=skipped, problems=problems)
