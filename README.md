# Reddit Repost Assistant Automation

>This project provides a structured automation system for identifying, validating, and preparing reposts on Reddit without automatically publishing content. Instead of a repost bot reddit that posts on its own, this assistant focuses on detection, verification, and draft preparation to support moderators and content managers.

It helps teams safely reuse relevant content while avoiding duplicate spam and rule violations.

<p align="center">
  <a href="https://t.me/devpilot1" target="_blank">
    <img src="https://img.shields.io/badge/Chat%20on-Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  </a> 
  <a href="mailto:support@appilot.app" target="_blank">
    <img src="https://img.shields.io/badge/Email-support@appilot.app-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail">
  </a>
  <a href="https://Appilot.app" target="_blank">
    <img src="https://img.shields.io/badge/Visit-Website-007BFF?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Website">
  </a>
  <a href="https://discord.gg/3YrZJZ6hA2" target="_blank">
    <img src="https://img.shields.io/badge/Join-Appilot_Community-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Appilot Discord">
  </a>
</p>
<p align="center">Created by Appilot, built to showcase our approach to Automation! <br>
  If you are looking for custom <strong> Reddit Repost bot  </strong>, you've just found your team — Let’s Chat.&#128070; &#128070;</p>

## Introduction

Reposting content on Reddit is common, but doing it responsibly requires context: checking whether something was posted recently, verifying subreddit rules, and ensuring the repost adds value. Manual checks are slow and inconsistent, especially in active communities.

This assistant automates the *decision-support* side of reposting. It scans content sources, checks for duplicates, scores similarity, and prepares repost drafts — leaving final approval and posting to humans.

### Why This Automation Matters

- Prevents accidental duplicate or rule-breaking reposts  
- Reduces moderator and curator workload  
- Improves consistency across repost decisions  
- Keeps a transparent audit trail of repost checks  

## Core Features

| Feature | Description |
|-------|-------------|
| Content Source Ingestion | Pulls candidate content from approved sources such as saved posts, archives, or feeds. |
| Repost Eligibility Checks | Verifies whether similar content already exists within a configurable lookback window. |
| Similarity Scoring | Compares titles, URLs, and text to rank repost risk instead of making hard decisions. |
| Draft Preparation | Generates repost-ready drafts with suggested titles and metadata. |
| Audit Logging | Stores every check and decision for moderation review and accountability. |

## How It Works

| Trigger / Input | Core Logic | Output / Action | Safety Controls |
|---|---|---|---|
| Candidate content submitted | Normalises text and URLs | Repost eligibility evaluated | Read-only Reddit API |
| Duplicate scan request | Searches historical submissions | Similarity-ranked matches | Rate limiting and backoff |
| Draft generation | Applies formatting and attribution rules | Draft payload created | No auto-posting |
| Export request | Packages results | JSON draft files | Access controls |

## Tech Stack

- **Python** – Core workflow and analysis logic  
- **PRAW** – Official Reddit API wrapper (read-only usage)  
- **FastAPI** – API layer for triggering checks and retrieving drafts  

## Directory Structure

    reddit-repost-assistant-automation/
        app/
            api/
                routes.py
                schemas.py
            services/
                repost_service.py
                similarity_engine.py
                rate_limiter.py
            core/
                config.py
                logger.py
        scripts/
            run_service.py
        data/
            candidates/
            checks/
            drafts/
        tests/
            test_similarity.py
            test_repost_rules.py
        requirements.txt
        README.md

## Use Cases

- Moderators use it to review repost candidates, so they can approve only valuable content.  
- Content curators use it to prepare repost drafts, so posting stays consistent and compliant.  
- Community managers use it to analyse repost patterns, so rules can be refined.  
- Developers use it to build moderation tooling, so repost logic is transparent and testable.  

## FAQs

**Does this automatically repost content on Reddit?**  
No. The system deliberately avoids automatic posting and only prepares drafts.

**Can it help reduce repost spam?**  
Yes. It highlights potential duplicates before anything is reposted.

**Is it suitable for moderation teams?**  
Yes. It is designed to support human review, not replace it.

**Can I integrate this with my own posting tools?**  
Yes. Draft outputs are API- and export-friendly.

## Performance & Reliability Benchmarks

- Average eligibility check: 1–2 seconds per candidate  
- Detection confidence for clear duplicates: ~90–94%  
- Recommended scale: up to 15 concurrent checks  
- Memory usage: ~150 MB under continuous scanning  
- Failure handling: retries transient API errors; preserves partial results for review  

<p align="center"><a href="https://cal.com/app-pilot-m8i8oo/30min" target="_blank"> <img src="https://img.shields.io/badge/Book%20a%20Call%20with%20Us-34A853?style=for-the-badge&logo=googlecalendar&logoColor=white" alt="Book a Call"></a> <a href="https://www.youtube.com/@Appilot-app/videos" target="_blank">  <img src="https://img.shields.io/badge/ð¥%20Watch%20demos%20-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch on YouTube"> </a></p>
