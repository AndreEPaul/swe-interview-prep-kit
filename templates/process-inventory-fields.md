# Process inventory: field guide

[process-inventory.csv](./process-inventory.csv) is an optional sheet for tracking your interview processes, one row per process (one company's whole loop). It can show you patterns in your own search, such as where processes tend to stall. It is not a scorecard, and a small number of rows proves little: report counts and the period you covered, and avoid concluding why something happened.

Fill only what you can source. Leave a cell blank or write `unknown` instead of guessing, and don't infer missing dates or outcomes. The suggested values are only suggestions. Use your own, as long as you use them consistently.

| Column | What it holds | Suggested values |
| --- | --- | --- |
| `process_id` | A label you choose. Avoid company names if you might share the file. | `p01`, `p02` |
| `role_track` | The kind of role, in your own words. | `frontend`, `backend`, `full-stack`, `management` |
| `start_date` | When the process began, such as the first recruiter contact. | `2025-03` or `2025-03-14` |
| `start_date_precision` | How exact `start_date` is. | `day`, `month`, `unknown` |
| `last_event_date` | The date of the most recent event in the process. | `2025-04-02` |
| `last_event_date_precision` | How exact `last_event_date` is. | `day`, `month`, `unknown` |
| `furthest_stage` | The latest stage you reached. Define your stage labels once and apply them the same way to every row. | `recruiter-screen`, `technical-screen`, `final-loop`, `offer` |
| `final_stage_reached` | Whether you reached the final stage of that process. Keep it separate from the outcome. | `true`, `false`, `unknown` |
| `outcome` | How the process ended. | `offer`, `rejected`, `withdrew`, `no-response`, `pending`, `unknown` |
| `outcome_as_of` | The date you last confirmed the outcome. Most useful for `pending` rows. | `2025-04-09` |
| `source_type` | Where the row's facts come from. | `recollection`, `calendar`, `recruiter-communication` |
| `notes` | Free text. Leave out anything private if you might share the file. | |

A synthetic example row, to show the format:

```csv
process_id,role_track,start_date,start_date_precision,last_event_date,last_event_date_precision,furthest_stage,final_stage_reached,outcome,outcome_as_of,source_type,notes
p01,frontend,2025-03,month,2025-04-02,day,technical-screen,false,rejected,2025-04-09,calendar,synthetic example row
```

Keep your filled file outside this repository; save only to a confirmed private path.
