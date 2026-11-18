# Expired-Supply Outlet Finder

A web app for **Blueprints for Pangaea (University of Michigan chapter)**. It finds organizations that can use expired medical supplies from Michigan Medicine so they don't end up in a landfill.

Expired supplies usually can't be used on patients, but they still work for **training**: nursing and medical simulation labs, EMT/paramedic programs, surgical-tech and vet-tech programs. A few surplus-recovery groups also run special programs that pass expired stock to schools and shelters. This app focuses on those organizations, starting with **Southeast Michigan** and then widening to the **Midwest**.

## What it does

- **Directory**: 44 researched organizations, each with a source link. Results are grouped by region (Southeast Michigan, then the rest of Michigan, then the Midwest, then national networks) and ranked by:
  - **Expired-supply policy**: *Takes expired* (a source confirms it), *Training use* (expired stock is normally fine; ask), *Ask first*, or *Unexpired only* (send good-dated stock)
  - **Supplies you have**: pick gloves, syringes, sutures and so on to see who can use them
  - **Distance**: straight-line miles from Michigan Medicine
- **Draft email**: writes an outreach email for any organization, worded for training sites or partners
- **Find new organizations**: builds web searches by program type (nursing sim labs, EMS programs, vet tech, shelters…) for each county or city, closest first. Organizations you add show up in the directory and can be exported as JSON.
- **Outreach tracker**: give any organization a status (To contact → Contacted → In conversation → Partner / Declined), add notes, and export a CSV for the Partnership Outreach team

Tracker progress and added organizations are saved in your own browser (localStorage). Export them to share.

## Run it

It's a static site with no build step and no dependencies.

- **Locally:** open `outlet-finder/index.html` in a browser.
- **GitHub Pages:** repo **Settings → Pages → Deploy from a branch → `main` / root**. The site will be live at `https://saitpally.github.io/teched/outlet-finder/`.

## Files

| File | What it is |
|---|---|
| `index.html` | The app (markup, styles and logic) |
| `data.js` | The organization directory. Edit this to add or correct entries |
| `README.md` | This file |

## Adding or correcting an organization

Add an object to `window.ORGS` in `data.js`:

```js
{
  id: "unique-id",
  name: "Example College Nursing Simulation Lab",
  kind: "training",          // training | partner | msro | animal | network
  sub: "Nursing simulation", // short description
  region: "semi",            // semi (SE Michigan) | mi | midwest | national
  city: "Novi, MI", lat: 42.48, lng: -83.47,
  expired: "training",       // confirmed | training | check | unexpired
  why: "One or two sentences on why they're a fit.",
  useful: ["syringes", "iv", "gloves"], // syringes iv gloves dressings catheters airway sutures surgical equipment lab
  contact: "Name, phone, email",
  web: "https://…",
  sources: ["https://…"]     // where the information came from
}
```

You can also add organizations in the app, click **Export additions**, and paste the JSON objects into `data.js`.

## Important caveats

- The directory was researched in November 2026 from public web pages. **Call or email to confirm an organization's policy before sending anything.**
- *Training use* means the program trains clinicians, where expired, unopened disposables are commonly used on manikins and task trainers. It does **not** mean the organization has agreed to take donations.
- Label expired items meant for training **"Not for human or animal use"**, and check what your institution requires before transferring supplies.
- Several large surplus groups (World Medical Relief, Global Health Ministries, Project C.U.R.E.) want supplies with a year or more of shelf life. They're listed as *Unexpired only*, which makes them good outlets for good-dated stock.
