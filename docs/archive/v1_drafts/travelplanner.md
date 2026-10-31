# Source: TravelPlanner

> **Dropped on 2026-10-30.** Kept for reference only; not part of v1. Do not build from it.

## 1. Source and pinned version

- TravelPlanner (Xie et al., ICML 2024). Dataset revision `8736504ecfc31b7f8b7e40122873c337e83fff7c`, code revision `e52c87f4ac348a3410c46dc3553c519db5ec5e23`, in `data/raw/travelplanner/`.
- Licenses: data CC-BY-4.0, code MIT.
- Splits used: **train (45) + validation (180)**. The test split (1,000) is not used: it does not include the constraint fields.
- Each query has structured fields: `org`, `dest`, `days`, `date`, `people_number`, `budget`, and `local_constraint` (house rule, cuisine, room type, transportation).
- Each query comes with `reference_information`: the closed database slice (flights, restaurants, attractions, accommodations with room type, house rules, and maximum occupancy) that the agent searches.

Role in v1: **planning with user preferences**, the User-type gaps.

## 2. What a seed is

One query from the **medium or hard** level. Easy queries are excluded: in both train and validation, every easy query has no local constraint, and every medium and hard query has at least one.

## 3. How gaps are found

No builder model. A gap is one **constraint field** that the query states. The field tells us which constraint it is; only the words that state it must be located (Section 4).

| Field | Values in the data | Use |
|---|---|---|
| `room type` | entire room, private room, shared room, not shared room | **Gap**, distinct values. The core gap for RQ3 |
| `house rule` | pets, smoking, parties, children under 10, visitors | One-way (see below) |
| `transportation` | no flight, no self-driving | One-way |
| `cuisine` | a list of 2–4 cuisines | Later. A list is messy to mask and score |
| `budget` | a dollar amount | **Excluded** ("choice you cannot see"): one plan can fit two budgets |
| `people_number` | 1–8 | Not used in v1 |

**Distinct vs. one-way.** Room type has distinct values: a plan's accommodation is one type, so the plan shows which value the agent used. House rule and transportation are **filters**: a plan that meets "pets allowed" also fits "no requirement", so only a violation shows anything. Compliance can happen by chance.

> **Open decision (one-way constraints).** Recommendation: use them as a separate group, reported apart from room type, and compare against how often plans meet the filter when no constraint is given.

**Alternatives** come from the field's own categories. For room type: `entire room` ↔ `private room`. `not shared room` covers both entire and private, so it is a filter, not a distinct value; treat it as one-way or exclude it.

## 4. Masking specifics

Queries are free text written from the structured fields, so the span that states a constraint must be located:

1. **Span finder:** regular expressions per field, or a tightly scoped model call ("quote the exact words that state the room-type requirement"). The model never chooses a gap; the field does.
2. **Python checks** that the quoted span appears word for word.
3. **Replacement:** one fixed neutral phrase per field, approved by the owner, that keeps the choice visible. Example for room type: "we have a preference about the type of accommodation".
4. Check 1 runs on every item.

> **Open item.** The owner approves the neutral phrase for each field before the build.

## 5. How Test B is decided

- **Test B:** `owner_rule` per field (table above). Room type passes.
- **Alternative availability, per item:** a **database check**, so that the alternative can actually show up in a plan: the destination's accommodations in `reference_information` must include at least one listing with the alternative room type (and the other stated house rules, and enough maximum occupancy for `people_number`). This reads the query's data; it runs no agent code.

`answer_source`: `user`. Preferences are stated by the user, and the database does not store them.

## 6. How Stage 2 observes the decision

`observable.where = "plan"`. Stage 2 runs TravelPlanner's own checker (`code/evaluation/hard_constraint.py`) on the agent's plan **twice**: once with the original value, once with the alternative. The result shows which value the plan satisfies. For room type, exactly one can hold. No judge is needed for the decision.

## 7. Known limits

- **A plan, not a booking.** The agent submits an itinerary; nothing is executed.
- **Queries are model-written** from the fields, so their wording is somewhat uniform.
- **One-way constraints** give weaker evidence (Section 3).
- **Small pool:** 150 medium and hard queries across train and validation, and fewer per field.
