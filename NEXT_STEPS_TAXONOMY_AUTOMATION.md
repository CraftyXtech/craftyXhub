# Next Steps: Taxonomy And Automation

Updated: April 6, 2026

## Current State

- Production taxonomy rename phase 1 has already been applied on `crafty-vps`.
- The migration used was [f1c9e7a4b2d0_rename_taxonomy_subcategories_phase1.py](/home/wetende/Projects/craftyxhub/api/alembic/versions/f1c9e7a4b2d0_rename_taxonomy_subcategories_phase1.py).
- The production database backup created before the rename is:
  - `/root/craftyXhub/backups/taxonomy_pre_rename_20260406T093212Z.json`
- Production Alembic head is now `f1c9e7a4b2d0`.
- Published-post safety check after migration:
  - `207` total posts
  - `204` active posts
  - `204` published active posts

## What Was Renamed In Production

- `Blockchain & Cryptocurrencies` -> `Blockchain & Crypto`
- `Automation & Smart Tools` -> `Automation`
- `Programming & Development` -> `Software Development`
- `Cybersecurity Basics` -> `Cybersecurity & Privacy`
- `Creator Economy & Monetization` -> `Creator Business`
- `Online Business Strategies` -> `Online Business & Marketing`
- `Career Development & Skills` -> `Career Growth & Job Search`
- `Online Learning Platforms` -> `Learning & Skill Building`
- `Productivity Hacks & Tools` -> `Productivity & Remote Work`
- `Remote Work & Digital Nomad` -> `Freelancing`
- `Personal Branding` -> `Personal Brand & Audience`
- `Mental Health & Psychology` -> `Mental Health`
- `Personal Growth & Self-Improvement` -> `Personal Growth`
- `Minimalism & Intentional Living` -> `Intentional Living`
- `Wellness & Work-Life Balance` -> `Work-Life Balance`

## Tag Reassignment Already Done

These tags were moved under `Productivity & Remote Work`:

- `Remote Work`
- `Work From Home`
- `Digital Nomad`
- `Async Work`
- `Home Office`

These tags were moved under `Freelancing`:

- `Freelancing`
- `Upwork`
- `Fiverr`
- `Consulting`
- `Copywriting`
- `UX Design`

## Important Safety Notes

- Category and subcategory names were changed in place.
- Category IDs and tag IDs were preserved.
- Category slugs were intentionally left unchanged.
- This means published posts were not detached from their categories or tags.
- Existing category URLs should still work because slugs did not change.

## Slug Warning

- Do not rename categories through the normal API update path unless the existing slug is passed explicitly.
- In [post.py](/home/wetende/Projects/craftyxhub/api/services/post/post.py#L1469), `update_category()` regenerates a slug when the name changes and `slug` is omitted.
- Future slug cleanup should happen only after redirect or legacy-slug support exists.

## Local Repo State

Local `main` is still dirty and should be parked before starting unrelated work.

Current local WIP includes:

- [ai.py](/home/wetende/Projects/craftyxhub/api/routers/v1/ai.py)
- [ai.py](/home/wetende/Projects/craftyxhub/api/schemas/ai.py)
- [__init__.py](/home/wetende/Projects/craftyxhub/api/services/ai/__init__.py)
- [taxonomy.py](/home/wetende/Projects/craftyxhub/api/services/ai/taxonomy.py)
- [post.py](/home/wetende/Projects/craftyxhub/api/services/post/post.py)
- [test_ai_router.py](/home/wetende/Projects/craftyxhub/api/tests/test_ai_router.py)
- [AiWriterPanel.jsx](/home/wetende/Projects/craftyxhub/frontend/src/components/ai-writer/AiWriterPanel.jsx)
- [AdminPostEditor.jsx](/home/wetende/Projects/craftyxhub/frontend/src/views/dashboard/Posts/AdminPostEditor.jsx)
- [f1c9e7a4b2d0_rename_taxonomy_subcategories_phase1.py](/home/wetende/Projects/craftyxhub/api/alembic/versions/f1c9e7a4b2d0_rename_taxonomy_subcategories_phase1.py)

There are also unrelated local changes not touched during this work:

- [postService.js](/home/wetende/Projects/craftyxhub/frontend/src/api/services/postService.js)
- [index.jsx](/home/wetende/Projects/craftyxhub/frontend/src/views/dashboard/Posts/index.jsx)

## Best Resume Order

1. Create a branch for the current local WIP.
2. Commit the taxonomy migration file so the repo matches production DB history.
3. Decide whether to keep the AI taxonomy suggestion changes on the same branch or split them into a second branch.
4. Avoid doing new unrelated work from dirty `main`.

## Next Taxonomy Tasks

1. Export the current post-rename taxonomy from production.
2. Build the canonical tag plan around generalized concepts, not vendor names.
3. Freeze slugs for now.
4. Decide the final canonical tag list and the tags to merge or retire.
5. Produce a full mapping sheet:
   - `old_tag`
   - `canonical_tag`
   - `target_subcategory`
   - `action`
6. Identify which tags can be renamed in place.
7. Identify which tags need merge migrations.
8. Reassign `post_tags` rows before deleting duplicate tags.
9. Re-check live tag usage counts after cleanup.
10. Review and backfill the active posts that still have no tags.

## Next Automation Tasks

1. Finish the DB-driven taxonomy suggestion work already started locally.
2. Make the backend read categories and tags from the database as the source of truth.
3. Return taxonomy suggestions with category, subcategory, tag IDs, and confidence.
4. Prefill those suggestions in the editor UI.
5. Allow manual override in the UI.
6. Add validation so selected tags belong to the correct taxonomy branch.
7. Add low-confidence fallback behavior when classification is uncertain.
8. Add publish-time validation for obviously mismatched taxonomy assignments.
9. Add tests covering taxonomy suggestion quality and validation rules.

## Good Follow-Up Work

- Add an admin taxonomy management screen.
- Add a report for unused tags and no-tag posts.
- Add a safe tag-merge tool that updates `post_tags`.
- Add redirect or legacy-slug support before any slug cleanup.
- Add public tag pages only after the canonical tag set is stable.

## Recommended Restart Point

When work resumes, start here:

1. Branch the current local WIP.
2. Commit the migration so repo history matches production.
3. Continue with the canonical tag mapping pass.
4. After taxonomy cleanup is stable, continue the automation pipeline.
