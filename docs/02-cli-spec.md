# CLI Spec (M1 MVP)

## cycle

* cycle create --cycle-id ... --name ... --start-day YYYY-MM-DD ... --end-day YYYY-MM-DD ... --tz Europe/Berlin
* cycle list
* cycle activate --cycle-id ...
* cycle close --cycle-id ...

## participant

* participant add --name "Last, First"
* participant list
* participant deactivate --name "Last, First"

## member

* member add --cycle-id ... --name "Last, First"
* member remove --cycle-id ... --name "Last, First"
* member list --cycle-id ...

### Membership State Changes

Membership commands create historical events.

Examples:

membership deactivate
membership reactivate

These commands do not overwrite previous status information.
Instead they create a **membership event** which becomes part of the participant's historical timeline.

Automatic system actions (auto-inactive or auto-reactivation via submission) also create events.

## checkin

* checkin record --cycle-id ... --name "Last, First" --points N \[--at "YYYY-MM-DDTHH:MM"]
* checkin import --cycle-id ... --csv path.csv

## admin

* admin correct --cycle-id ... --name "Last, First" --score-day YYYY-MM-DD --points N --reason "..."
* admin reactivate --cycle-id ... --name "Last, First" [--effective-day YYYY-MM-DD] --reason "..."
* admin apply-auto-inactive --cycle-id ... --through YYYY-MM-DD

## report

* report leaderboard --cycle-id ... --from YYYY-MM-DD --to YYYY-MM-DD
* report export --cycle-id ... --from ... --to ... --out out/leaderboard.csv
* report whatsapp --cycle-id ... --from ... --to ...
