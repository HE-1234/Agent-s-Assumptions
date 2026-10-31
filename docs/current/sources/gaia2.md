# Source: Gaia2 (ARE), execution split

> **Status: in force** (adopted 2026-10-31). Chosen on 2026-10-30 as the assistant-style source. Follows the general method in `../stage1_method.md`. Facts marked *(seen)* were checked in the data.

## 1. Source and pinned version

- Gaia2, from Meta's Agents Research Environments (ARE), Hugging Face dataset `meta-agents-research-environments/gaia2`, **execution** configuration.
- 160 scenarios in the validation split *(seen: `num_rows_total` = 160)*. All sampled rows carry the tags `Universe` and `Execution` *(seen)*.
- Licenses: data CC-BY-4.0 *(seen on the dataset card, which also states Llama-output and third-party-content terms)*; ARE code MIT.
- **Pinned and downloaded:** revision `78ea3bdbdeec2bdcd6afa5420915d8a22f23ed99`, in `data/raw/gaia2/` (execution Parquet, 162 MB), with hashes in `data/raw/gaia2/source_index.json`. Each scenario carries the full state of a simulated phone.
- **Draw:** 30 scenarios (`PILOT_V1_PLAN.md`).

Role in v1: the **assistant-style** source: errands over shopping, cabs, calendar, contacts, email, messages, and apartment listings, written as single requests to an assistant.

## 2. What a seed is

One scenario. Its parts *(seen)*:

- **The instruction:** the `content` of the one `USER` event (`AgentUserInterface.send_message_to_agent`).
- **The correct actions:** the `OracleEvent` entries of type `AGENT`, each with an app, a function, and argument values (for example, `Contacts.add_new_contact` with `first_name = "Anna"`; `Calendar.delete_calendar_event`; `RentAFlat.save_apartment`).
- **The app state:** the starting data of each app (12 apps in the samples: Files, Contacts, Messages, Chats, Emails, Calendar, RentAFlat, City, Cabs, Shopping, and others).

Examples of instructions *(seen)*:

- "Order 1 of the red metal Disney Pixar Cars Deluxe Van Scanlane and 1 of the cardboard … Cutouts."
- "Book a Premium cab for 30 minutes before the photoshoot today, from Home to …"
- "Add new contact - Anna Zoher, from Berlin, Germany, 28 y.o., musician, phone number … Schedule wedding on November 16th from 7 am till 2 am next day at Central …"

**Seed screening** (the builder skips these; the owner reviews skips):

- **Filter puzzles,** where the instruction is a search rule rather than an errand with stated details. Example *(seen)*: "Find zip codes with a violent crime rate from 5 to 10. Find all properties with those zip codes and save them…".
- **Bundles:** many instructions chain several errands (reply to an email, delete an event, order items). This is fine: each item still deletes **one** detail from **one** errand.

**Excluded before the draw: invitations to ask (decided).** A sentence like "Let me know if are unsure about anything before proceeding" changes how likely an agent is to ask, so these scenarios are excluded. One was found *(seen)*: `pilot/runs/pilot_v1/gaia2_invitation_exclusions.json`. Requests for a completion report, or for questions to third parties, are not invitations.

## 3. How gaps are found

A **builder model** proposes gaps (`../stage1_method.md`, Section 3), applying Test B and the fail rules and guided by LHAW's dimensions. No code runs (D8).

**What the builder reads for each scenario:**

1. The instruction.
2. The correct actions and their argument values.
3. The app records those actions touch (for example, the product's variants in Shopping, the cab service tiers in Cabs, the calendar events on that day), so it can check that the alternative value really exists and would change the result.

Typical gaps, for orientation (the builder decides per scenario):

| Detail | Example | Lands in |
|---|---|---|
| Quantity | "Order **1** of …" | `quantity` argument |
| Product variant | "**red metal**", "**cardboard**" | Which item / variant is ordered |
| Service tier | "a **Premium** cab" | Cab service type |
| Time | "**30 minutes before** the photoshoot"; "from **7 am** till **2 am**" | Booking / event times |
| Contact details | "**28** y.o.", "**musician**" | Contact fields |
| Target | "**Aurélie Dumont's** emails" | Which records are changed |

**Alternatives:** the builder should prefer a value that exists in the app state (for example, another variant of the same product, another cab tier).

## 4. Masking specifics

- Python deletes the builder's exact spans. Example: "Order 1 of the red metal Disney Pixar Cars Deluxe Van" → "Order 1 of the Disney Pixar Cars Deluxe Van".
- Replacement text only where the deletion breaks grammar.
- Check 1 runs on every item.

## 5. How Test B is decided

By the builder, in its prompt, with a one-sentence reason, using the correct actions and the app records (Section 3). The owner reviews.

`answer_source`: mostly `user`. Some details may also be in the app state (for example, a contact's saved address); then it is `both`, and the builder says where the value is stored.

## 6. How Stage 2 observes the decision

`observable.where = "db_state"`. Stage 1 stores the correct actions for the original value (`observable.original_outcome`). Stage 2 compares the agent's write actions or final app state with them. The outcome under the alternative is not precomputed (no code in Stage 1).

Stage 2 must run the scenarios: either inside the ARE framework, or with a lighter harness of our own over the same app state and tools. Gaia2 has no confirmation policy that blocks the offline-user condition (to be confirmed).

ARE already has a hook for a simulated user *(seen in the ARE 1.2.0 package, not yet run)*: `send_message_to_user` passes the agent's message to an attached `UserProxy` (one method, `reply(message) -> str`) and returns its reply. So Stage 2 can keep ARE and its apps unchanged and attach a proxy that calls the user simulator (online) or returns the fixed offline message. Note that Gaia2 uses the same tool for the agent's final report, so Stage 2 must separate questions from reports.

## 7. Known limits

- **Heavy setup** for Stage 2: the ARE framework, and large per-scenario state.
- **Small pool:** 160 scenarios, fewer after screening out filter puzzles.
- **Related prior work:** Gaia2 has its own "ambiguity" split, which studies unclear requests. Cite it and say how single-detail deletion differs.
- **Verifier details unconfirmed:** how ARE's own checker compares arguments (exact or judged by a model) was not checked. Its `validation/` code has both a tool judge and an event judge.
- **Time-dependence:** scenarios have start times (Unix timestamps in October 2024). Relative times like "today" and "30 minutes before" depend on them.
