---
slug: google-ads-api-competitive-benchmarks-2026
title: "Google Ads API v25.2: How to Use Competitive Benchmarks"
metaTitle: "Google Ads API v25.2: Competitive Benchmarks"
description: "Google Ads API v25.2 adds competitive percentile benchmarks and Performance Max controls. Learn what the update enables and how to turn comparison into action."
keywords: ["Google Ads API v25.2", "Google Ads competitive benchmarks", "Performance Max API"]
category: "AI & Automation"
date: "2026-09-26"
readMins: 7
excerpt: "Google Ads API v25.2 adds percentile-based competitive benchmarks and new Performance Max controls. Here is how marketing teams can use the update as context for better questions—not as a substitute for their own campaign data."
---

## What changed in Google Ads API v25.2

Google Ads API version 25.2 brings several additions for developers and advertisers, including percentile-style competitive benchmark data, a way to create a Performance Max draft from an existing Smart campaign, and new URL-tracking controls at the asset-group level. Google released the version on September 23, 2026, according to the [official release notes](https://developers.google.com/google-ads/api/docs/release-notes) and [Search Engine Land’s coverage](https://searchengineland.com/google-ads-api-v25-2-adds-competitive-benchmarks-and-pmax-upgrades-491541).

The most useful takeaway for marketers is not that one metric will suddenly reveal a winning strategy. It is that campaign teams using a compatible API connection can add a relative reference point to their analysis, while developers get more programmatic control over certain campaign workflows.

This is a developer-facing update: accessing these additions means working through the Google Ads API and the software or integration that connects to it. Teams using the Google Ads interface alone should not assume every API feature automatically appears as a new button in their account. For marketing leaders, the practical question is whether a reporting or campaign-management tool they already use will expose the new fields and controls.

## What a competitive benchmark percentile can tell you

The v25.2 update adds percentile benchmark data through Google’s BenchmarksService. As described in the release coverage, an API request can compare an advertiser’s position against an “all advertisers” benchmark and apply category filters. That gives a team another way to put its own campaign numbers in context.

A percentile is a **relative comparison**, not a verdict on campaign quality. It does not by itself explain why a campaign is performing a certain way, whether its cost is sustainable, or whether its results are valuable to the business. The useful interpretation is narrower: “How does this selected measure compare with the selected reference group under these filters?”

That distinction matters. A campaign can compare favorably on one metric and still be inefficient against the business objective. Conversely, a lower relative position may be acceptable if the campaign reaches a strategically important audience or generates customers with stronger downstream value. Your own goals, measurement setup, and conversion data still determine whether performance is working.

## A practical workflow for using Google Ads competitive benchmarks

Before incorporating Google Ads competitive benchmarks into a report, agree on the question the comparison should help answer. For example, a team might want to understand whether a particular campaign metric is unusual relative to a selected category, or decide which campaign deserves a closer diagnostic review. Avoid treating the percentile itself as an optimization instruction.

A measured workflow helps keep the benchmark useful:

1. **Choose one business question.** State whether you are investigating reach, cost, conversion activity, or another metric available in your reporting setup. Do not bundle unrelated questions into a single benchmark review.
2. **Confirm the comparison context.** Record the category filters used and the date range for the account data. If the context changes, note that before comparing the results with an earlier report.
3. **Review your own trend first.** Look at the account’s performance over comparable periods. The benchmark can add outside context, but it should not replace the account’s own history.
4. **Check measurement quality.** Confirm that conversion definitions, attribution settings, landing pages, and tracking have not changed in a way that makes the comparison misleading.
5. **Investigate, then test.** If the relative position raises a question, inspect the campaign and audience details, choose a specific change, and evaluate it against a defined business outcome.
6. **Write down the caveat.** Include the comparison filters and the limits of the data alongside any conclusion shared with stakeholders.

This approach is especially useful when the benchmark becomes part of a dashboard. A percentile without its context can look more definitive than it is; a percentile beside the relevant filters, period, and account trend is easier to interpret responsibly.

## Do not turn a relative position into an automatic bid change

A benchmark can suggest where to look, but it cannot independently tell an advertiser what bid, budget, keyword, or creative to change. For example, a team that spots an unfavorable comparison should first check whether the campaign’s purpose, audience, geographic settings, and conversion measurement match the comparison context.

Then consider possible explanations as hypotheses—not proven causes. Is the campaign reaching the intended search audience? Did the landing page or offer change? Are conversion events being recorded consistently? Did an account structure or budget adjustment alter the comparison period? Each question calls for a different investigation, and a percentile alone cannot distinguish among them.

When a change is warranted, make it testable. State what will change, what outcome should improve, what period will be reviewed, and what other factors could influence the result. Keep the benchmark in the diagnostic role; use your campaign and business data to assess the actual impact.

## How the Performance Max additions fit into the update

Version 25.2 also adds a method that can generate a Performance Max draft from an existing Smart campaign. The word **draft** is important: treat the result as a starting point for review, not as a finished campaign that should be published without checking its settings, assets, destination, and measurement.

The release coverage also describes new AssetGroup-level controls for tracking templates, custom URL parameters, and final URL suffixes. For teams managing multiple asset groups, these options create more places to configure URL tracking within a Performance Max setup. Before changing a live workflow, document how the account currently appends tracking information and test the resulting destination URLs to avoid inconsistent analytics.

These features are separate from the benchmark data, but they share a theme: version 25.2 gives API-connected teams additional visibility and campaign-management options. Each is most useful when it fits a clear process—reporting comparisons for diagnosis, and reviewing generated drafts or tracking settings before they affect live traffic.

## Implementation checklist for marketing teams and developers

If you rely on an agency, analytics vendor, or internal engineering team for Google Ads API access, use the release as a short coordination checklist:

- Ask whether your current reporting or campaign-management integration supports API v25.2 and its new benchmark fields.
- Confirm how the benchmark category filters and time period will be displayed in reports.
- Agree on which campaign metrics are useful for comparison and which business outcomes remain the primary decision criteria.
- Review how your organization handles campaign changes generated through the API, including human approval before publication.
- Test new tracking settings in a controlled workflow and verify the landing URL and analytics parameters.
- Keep a record of client-library and application updates made to adopt the new version.

Search Engine Land notes that using the new capabilities requires updating client libraries and client code. That means the timing of availability in a particular dashboard depends on the software and integration supporting it. Confirm the implementation with the team that maintains your connection rather than assuming a feature is already enabled.

## FAQ: Google Ads API v25.2 and benchmarks

### What is new in Google Ads API v25.2?

The release adds percentile benchmark data through BenchmarksService, a method to create a Performance Max draft from a Smart campaign, and AssetGroup-level controls for URL tracking.

### Do competitive benchmarks show exactly what a competitor is doing?

The described feature compares an advertiser’s position with an “all advertisers” benchmark and supports category filters. It is a comparative reference, not a report identifying an individual competitor’s campaign.

### Does a low percentile mean I should raise my bids?

Not on its own. First check the selected comparison context, the campaign’s goal, measurement quality, and your own business results. Use the comparison to prompt analysis, not as an automatic bid rule.

### Can every advertiser use the new API features immediately?

The additions are accessed through the Google Ads API. Teams should check whether their API integration, client libraries, and reporting tools have been updated to support them.

Zapplon offers AI agents, AI video, and performance marketing services to help businesses connect automation with practical campaign workflows. [Contact Zapplon](/contact) to discuss your goals. **Services start at $50.**
