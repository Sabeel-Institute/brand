---
name: sabeel-app-stores
description: How Sabeel Institute's phone apps (the LMS, Kanban, the Time Tracker) reach phones and get through App Store and Google Play review — the decisions that keep review simple (the phone apps never create accounts, one reviewer's email door, content that belongs to the institute, adults only), how we answer each store's questions, the shared Apple and Play accounts, keys and tester lists, the review notes, and the submission checklists. Use when releasing, submitting or answering a store questionnaire for any Sabeel app, and before any change to sign-in, accounts, posting, privacy or signing.
---

# Sabeel apps on the App Store and Google Play

Three apps, one method. This skill is the method and the decisions every Sabeel
app shares. Each app's repository has its own `docs/STORE-RELEASE.md` with that
app's answers, its review account and where it stands; its `docs/DEPLOY.md` and
`docs/IOS-BUILD.md` say how to build and ship it. When the two disagree about a
shared decision, this skill wins, and the app's file is the one to fix.

The latest version is in
[Sabeel-Institute/brand](https://github.com/Sabeel-Institute/brand) under
`skills/sabeel-app-stores/`. Change a shared decision here first, then in each
app.

## The apps

| App | Repository | Who uses it | How they sign in |
|---|---|---|---|
| Sabeel Institute LMS | `Sabeel-Institute/lms` | Staff and students (all adults) | Staff: Google Workspace (`@oursabeel.com`). Students: email and password accounts that staff create |
| Sabeel Kanban | `faisal-shah/sabeel-institute-kanban` | Staff | Google Workspace |
| Sabeel Time Tracker | `faisal-shah/sabeel-institute-time-tracker` | Staff and volunteers with `@oursabeel.com` accounts | Google Workspace |

Each app also has a web app, which is where accounts are made.

| | iPhone | Android |
|---|---|---|
| Now | TestFlight, internal testers only | Google Play internal testing, plus an APK on the app's download page |
| Destination, every app | The App Store, **unlisted**, after App Review. Kanban goes first and alone; the others follow once it is through | Google Play **production**, a public listing (Play has no unlisted) |

Decided by Faisal on 2026-10-16: every app goes to the unlisted App Store and
to public Play production, and stays on TestFlight and Play internal testing
until then.

## The decisions

### 1. The phone apps never create an account

> The mobile app must never cause an account to come into existence.

Both stores require account deletion **inside the app** only if the app
supports account creation:

- Apple 5.1.1(v): "If your app supports account creation, you must also offer
  account deletion within the app."
- Google Play: an app supports account creation "if a user can complete
  creating an app account directly in the app **or if the app directs the user
  to an app account creation flow outside of the app**."

Satisfy neither and the requirement is not engaged. That spares us a deletion
flow that would have to decide what happens to the institute's records when a
person deletes themselves, which is the hard part, not the button.

How every app keeps it (decided 2026-08-18; Android and iPhone alike):

- A Google sign-in asks the server first. The `accountExists` callable checks
  the Google ID token and answers one yes or no; only a yes reaches
  `signInWithCredential`. Signing in to an account that already exists creates
  nothing.
- No account is created in the app, by any path. Accounts are made on the web
  (staff sign in there and wait for an admin's approval) or by staff (students).
- **The refusal names no website**, because Play's second clause forbids
  pointing at a sign-up flow: "This account isn't set up for the app yet.
  Contact your administrator." The real instruction goes in the onboarding
  email. No "Sign up" link, ever; each app's sign-in code says why.
- A Workspace login is a credential, not the app account. The app account is
  the Firebase Auth record and the user document the backend makes.

Each app's `docs/STORE-RELEASE.md` names the code that holds this and the tests
that prove an unknown account creates nothing.

### 2. Sign in with Apple is not required

Guideline 4.8 exempts an app that "exclusively uses your company's own account
setup and sign-in systems" (the LMS's student accounts) and an "education,
enterprise, or business app that requires the user to sign in with an existing
education or enterprise account" (Google Workspace). If a student path ever
offers a third-party login, Sign in with Apple becomes mandatory.

### 3. Store reviewers get one ordinary account, through an email door

Decided by Faisal on 2026-10-15:

- "sign in thru email should never be able to be an admin or manager. Just a
  member."
- "That sign in with password for kanban and timesheet should only accept that
  one email. The sign in page shouldn't indicate its a special thing for a
  reviewer."
- Reviewer data through ordinary means — "That way there's no special code for
  app reviewer."

So:

- **The address is `apps-reviewer@oursabeel.com` in every app** (the
  Workspace accounts and groups the apps use are named `apps-…`). In Workspace it
  is a group, never a user: it receives mail, and nobody can sign in to Google
  as it. A reviewer cannot use a Workspace account: Google's
  login challenge on an unfamiliar device can only be waived by an admin for
  ten minutes, and review happens days later.
- **Kanban and the Time Tracker:** a plain "Sign in with email" link under the
  Google button, with nothing about reviewers. The server accepts a password
  sign-in for that one address only (blocking functions `beforeSignUp` and
  `beforeSignIn`, which need the project on Identity Platform), refuses every
  password sign-up from a client, and treats a password session as an
  ordinary member whatever its claims say, in the rules and in every callable.
  An admin makes the account with the Admin API; no blocking function sees
  that.
- **The LMS:** the reviewer is an ordinary student, the only student of an
  "App Review" cohort, through the students' existing email door.
- **Sample data comes through the app's own admin screens**: an "App Review"
  board in Kanban, the cohort with a sample class in the LMS, nothing in the
  Time Tracker (its reviewer is a member whose approver is Faisal).
- **The password** lives only in the owner's vault and, at submission, in App
  Store Connect's App Review Information sign-in fields and Play Console's App
  access. Never in a repository, a chat or a log.
- **Keep it alive.** Apple: the demo account "must not expire", and every
  update is reviewed again. Data that ages (the LMS's due dates) is renewed
  before each submission.
- Apple asks for credentials for each account type. Staff roles here are
  granted only to the institute's Workspace accounts, which a reviewer cannot
  use; the review notes say so and describe what staff can do. If a reviewer
  still asks for staff access, answer with a short video of the staff screens
  (the LMS's staff help films are one), Apple's usual alternative, not a
  password account with a staff role.

### 4. Content belongs to the institute: rules and a report, no blocking

People post in every app: cards, comments and attachments (Kanban), hours and
notes (the Time Tracker), assignments, hand-ins, files and feedback (the LMS).
Both stores treat that as user-generated content:

- Apple 1.2 asks for a way to filter objectionable material, to report it, to
  "block abusive users from the service", and published contact details, and
  has no exception for closed, institutional apps.
- Google Play defines user-generated content as content "visible to or
  accessible by at least a subset of the app's users" (not "public" users),
  and names this case: apps "exclusively used within a specific school or
  company" must provide "in-app functionality to report content and users",
  and users accept terms before posting. Blocking is required for "1:1 user
  interaction with specific users (for example, direct messaging, tagging,
  mentioning)". The policy has no exemption for enterprise, internal or
  private apps (checked against the policy page, 2026-10-16); advice that
  closed apps are exempt is wrong.

These apps are not public forums. Nobody can sign up through them, everything
posted is seen only by members an admin put in the same class, board or team,
and all of it is subject to the institute's rules. Blocking between members
would break the work: a student who blocked a teacher would stop receiving
assignments. So, decided by Faisal on 2026-10-16, **each app adds two things**:

1. **The institute's rules, accepted once.** One screen at first sign-in,
   before anything can be posted, with an "I agree" button:

   > **Before you continue.** [App] is for Sabeel Institute's staff [and
   > students], and what you post is seen only by members of your class, board
   > or team. By continuing you agree to the institute's rules: post only what
   > belongs to your work or class, and nothing abusive, harassing, hateful,
   > sexual or otherwise objectionable. The institute does not tolerate either.
   > Administrators may remove content and suspend accounts that break these
   > rules. To report something or someone, use **Report a problem** in
   > [More / Settings]; administrators respond within 24 hours.

   The rules state no minimum age: a stated age above Apple's calculated
   rating forces the rating up.
2. **"Report a problem"** under More (or Settings): the person says what or
   who they are reporting (the item or the person, and what is wrong, in their
   own words). The app's server emails it from `apps-noreply@oursabeel.com`
   ("Sabeel Apps No Reply") to the group **`apps-reports@oursabeel.com`**, with
   Reply-To set to the reporter, and keeps a copy in the database as a record; nobody reviews
   reports inside the apps. (`abuse@` is reserved by Google Workspace.) The
   administrators answer within 24 hours by removing the content or disabling
   the account. Naming the item or
   person meets Play's "report content and users" to the letter. The 24 hours
   is a promise the institute keeps.

And deliberately not:

- **No blocking between members.** Abusive users are blocked "from the
  service" by an administrator disabling the account, which signs them out and
  keeps them out. The review notes say why per-member blocking is not offered.
- **No automatic removal and no word filter.** Only institute-made accounts can
  post, and administrators remove content.

Both go in before an app's first App Store submission or Play production
release, whichever comes first. While an app is only on TestFlight's internal
testers and Play internal testing, neither store reviews this.

If Apple still rejects under 1.2: reply in App Store Connect quoting "block
abusive users from the service", ask for a call, appeal; only then add a
per-person **Mute** that hides that person's comments and notifications and
never assignments, grades, feedback or class materials. Google has accepted
mute in place of blocking; Apple's view of it is untested. Putting "Report a
problem" also in each post's ⋯ menu, carrying the post and its author, is the
next step if a reviewer wants reporting closer to the content.

### 5. Adults only

Every user is an adult: staff, volunteers and students. No app has users under
13, so COPPA does not apply. Say so in each store's age and audience questions
(below) and in the privacy policy.

Open: Texas SB 2420 (app-store age verification) has been in force since
2026-06-04, with no exemption found for nonprofit or education apps. Whether it
reaches TestFlight or unlisted installs, and what it asks of a developer whose
users are all adults, is a question for a lawyer before the first public
listing.

### 6. Privacy

- **Each app's web app serves `/privacy` and `/support` as static pages**,
  outside the signed-in app, so a reviewer or a store crawler fetching them
  anonymously gets the page, not an empty app shell. The privacy page carries no
  navigation and no sign-in link.
- **Inside each phone app, a privacy link** on the sign-in screen (where a
  reviewer who has not signed in can reach it, Apple 5.1.1(i)) and in settings.
  **Not the support page:** it tells newcomers to sign in on the website first,
  and a phone app pointing there is the account-creation pointer decision 1
  forbids. The support URL goes in the store listings only.
- **Deletion by email**, to **`privacy@oursabeel.com`**, one address for every
  app (decided 2026-08-18): a Workspace group (created 2026-10-16, Faisal its
  owner and member), which anyone on the web may email. The policy states the process and the time it takes, and that
  institutional records (cards, timesheets, academic records) are kept as the
  institute's records while the account and personal data are removed.
- **Every third party is named**: Google (sign-in), Firebase and Google Cloud,
  Cloudflare (the LMS's media), Sentry (crash reports), Apple (iPhone
  notifications), Zoom (the LMS's imports).
- **Store answers match the policy.** Google checks Data safety against it.
  Crash reporting inside the app is not tracking: no App Tracking Transparency
  prompt.

### 7. The legal position

Driven by the store rules, not by statute:

- Texas TDPSA: nonprofits are exempt.
- CCPA: applies to for-profit businesses only.
- FERPA: **does not apply** (confirmed 2026-08-18: the institute receives no
  Department of Education funding). Student records are kept on institutional
  and contractual grounds. Do not cite FERPA.
- GDPR: out of scope; all students are in the US. Revisit if the institute
  enrols anyone in the EU or UK.
- COPPA: no users under 13.

### 8. Play signs with the app's own key

The LMS and the Time Tracker are signed by Play with **their own release
keys**, so an install from Play and the APK from the download page update each
other. Kanban took a Google-generated key in August: Play installs and its
download-page APK cannot replace each other (uninstall first).

Play Console now gives **every new app a Google-generated key the moment it is
created**. To use the app's own key: App integrity → App signing → **Change
key** → "Export and upload a key from Java keystore". Play gives an encryption
key **per app**; Google's PEPK tool wraps the keystore's key with it, and the
zip is uploaded on the same page. This must happen before any release reaches
open testing or production. APKs Play generated from a bundle uploaded before
the change stay signed with the old key, so each app's `publish:play` script
completes a release only after checking the APKs Play generated carry the
app's own certificate.

### 9. Distribution

- **iPhone now: TestFlight internal testing.** Up to 100 App Store Connect
  users, no review, each build expires after 90 days. Staff are invited to App
  Store Connect (Developer role), accept, and are then added to the app's
  internal group, which gets every build.
- **iPhone next: the App Store, unlisted.** A full App Review once, then a link
  that is not searchable, with no expiry and no install cap. The Account Holder
  files Apple's unlisted request after the app is submitted, and the app must
  not be a beta. A public listing for an institution-only app risks a 3.2
  rejection; unlisted is the route Apple intends.
- **Android now: Google Play internal testing**, with the account-wide email
  list "Sabeel staff" ticked on each app's Internal testing → Testers page.
  Testers join through that page's link (Play sends no email). Up to 100
  testers. Internal tests "might not be subject to standard Play policy or
  security reviews".
- **Android next: Google Play production**, a public listing, since Play has no
  unlisted. Production is fully reviewed against Play's policies, including
  the content rules in decision 4. The developer account is an organisation,
  so the 12-testers-for-14-days rule does not apply. Play requires blocking
  only for direct messages and mentions ("tagging, mentioning"). Decided by
  Faisal on 2026-10-16 for Kanban's @mentions: argue first. Blocking is all or
  nothing: there is no per-person block; a person who wants someone stopped
  reports them, and an administrator disables that account, which removes them
  from the service entirely. Mention notifications can also be turned off
  altogether. A per-person "mute mentions from this person" is built only if
  Google objects.

### 10. Small things each store checks

- **Export compliance:** `ITSAppUsesNonExemptEncryption` is false in every
  app (HTTPS only), so no build asks.
- **Privacy manifest:** `expo.ios.privacyManifests` in `app.json`; Google's
  sign-in pods bring their own manifests. Watch for `ITMS-91053` emails after
  an upload.
- **Xcode and SDK:** uploads must be built with Xcode 26 and the iOS 26 SDK
  (GitHub's `macos-26` runners).
- **Play target API:** 36 (each app's Gradle config).
- **Android developer verification** (worldwide in 2027): an APK installed from
  outside Play needs its package and signing key registered in Play Console.
  Play registers its own apps.

## How we answer the questionnaires

Each app's `docs/STORE-RELEASE.md` records the final answers; these are the
shared ones.

**Apple App Privacy:** data linked to the user, none used for tracking: contact
info (name, email), user content (the app's own content), identifiers (user
id), diagnostics (crash data). Add photos or files where the app takes
attachments, and audio/video for the LMS's recordings.

**Apple age rating:** user-generated content Yes, messaging and chat Yes where
the app has comments or feedback, social media No (no feed), advertising No.
Keep the rating Apple calculates (expected 4+). The institute's rules state no
minimum age; a minimum age in an app's terms would oblige an override to it.

**Play Data safety:** account creation **No** (true by decision 1), so the
deletion questions fall away. Data collected matches the privacy policy;
encrypted in transit; deletion by request.

**Play content rating (IARC):** answer the user-interaction question Yes; it
adds an "Users Interact" notice, not a higher age.

**Play target audience:** 18 and over only. No ads.

**Play App access:** the review account and its password, with a sentence on
where to sign in with it ("Sign in with email" in Kanban and the Time Tracker,
the Students form in the LMS).

## Review notes

Paste into App Store Connect's App Review Information notes (and, adapted, into
Play's App access instructions):

```text
This app is for the staff [and students] of Sabeel Institute, a nonprofit
adult-education institute. Accounts are provisioned by the institute through
its web application; the app refuses any identity that does not already have
an account, and no account is created from the app. Guideline 5.1.1(v) is
therefore not engaged.

Staff sign in with the institute's Google Workspace accounts (the
education/enterprise exemption under Guideline 4.8). [LMS: Students sign in
with first-party email and password accounts that staff create.]

For review, use ["Sign in with email" | the Students form] with the account
below. It is an ordinary
[member | student] account made by an administrator. [App-specific: what it
can see and do.] Staff and administrator roles are granted only to the
institute's own Workspace accounts.
Email: apps-reviewer@oursabeel.com   Password: <from the vault>

All content is visible only to members an administrator has added to the
same [class | board | team]. Nothing is public, searchable or discoverable,
and users cannot contact strangers. Guideline 1.2:
- Terms: every user accepts the institute's rules, which prohibit
  objectionable content and abusive users, before they can post.
- Reporting: More > Report a problem. The report goes to the institute's
  administrators, who act on it within 24 hours by removing the content and
  disabling the author's account.
- Blocking abusive users from the service: administrators disable the
  account, which signs it out and stops it signing in. Blocking between
  members is not offered because the app carries required [coursework | work]:
  [a student who blocked a teacher would stop receiving assignments].
- Contact: [support URL] (the privacy policy, linked on the sign-in screen,
  gives the same address).

Account deletion is requested by email; the privacy policy (linked on the
sign-in screen) states the address, the process and what is retained.
```

## Submitting

**iPhone (App Store Connect), once per app:** the app's TestFlight build
checked on a phone first; App Privacy; age rating; description, keywords,
category, support URL and privacy policy URL; screenshots at the required
sizes; App Review Information (contact, sign-in required, the review account,
the notes above); manual release. Then the Account Holder files the unlisted
request.

**Android (Play Console), before production:** App content (privacy policy
URL, App access, ads, content rating, target audience, Data safety); the store
listing (short and full description, icon, feature graphic, phone
screenshots, category, contact email); then a production release, which Play
reviews.

## Shared accounts and assets

| What | Detail |
|---|---|
| Apple Developer | Organization account "Sabeel Institute", team `XRKWA4QRN9`. Account Holder: Faisal (`faisal.shah@oursabeel.com`) |
| App Store Connect | LMS app 6823374038 (SKU `sabeel-lms`), Kanban 6801011482, Time Tracker 6823429437. Staff testers are App Store Connect users with the Developer role |
| Apple Distribution certificate | One, shared by the three apps' GitHub builds, expires **2027-10-16**; one App Store profile per app. Renewal: each app's `docs/IOS-BUILD.md` |
| App Store Connect API key | Admin role; builds, signs and uploads without a person signing in. Held in the owner's vault |
| Apple push key | One key (`X5R8FL94BC`) for every app of the team, the `APNS_KEY` secret in each Firebase project |
| Google Play | Organisation developer account. Publishing service account `sabeel-play-publisher@sabeel-institute-kanban.iam.gserviceaccount.com`, given "Release apps to testing tracks" per app; it cannot release to production until Play Console also gives it "Release to production" for that app (or the release is promoted in the console) |
| Play testers | The email list "Sabeel staff", account-wide, ticked per app |
| Reviewer address | `apps-reviewer@oursabeel.com`: the reviewers' login inside each app; in Workspace a **group** (so the address receives mail, such as a set-password link) and never a user, so nobody can sign in to Google as it |
| Privacy address | `privacy@oursabeel.com`, a group anyone may email; Faisal its only member (his choice, 2026-10-16) |
| Reports address | `apps-reports@oursabeel.com`, a group; "Report a problem" emails land here; Faisal its only member |
| Sender | `apps-noreply@oursabeel.com` ("Sabeel Apps No Reply"), a Workspace user nobody signs in to. Each app's server sends as it through domain-wide delegation, scope `gmail.send` only, with no password or key: service accounts `report-mailer@<project>.iam.gserviceaccount.com` in `oursabeel-lms`, `sabeel-institute-kanban` and `sabeel-institute-time-tracker`, each authorised in the Admin console's Domain-wide delegation. Each project has the Gmail API on, and whatever sends (the app's function) needs `roles/iam.serviceAccountTokenCreator` on its project's `report-mailer` to sign the delegation token. Proved 2026-10-16: each sent a test to `apps-reports@` |

Secrets (keystores, keys, the reviewer's password) live in the owner's vault,
never in a repository.

## Open decisions

- Texas SB 2420 (decision 5): ask a lawyer before the first public listing.
- Who reads each privacy policy who did not write it.
- Store listing copy, screenshots and category, per app.
