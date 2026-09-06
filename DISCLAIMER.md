# DISCLAIMER & TERMS OF SERVICE

**ai4sustainablex** is provided by SustainableX (https://sustainablex.in, info@sustainablex.in).

## 1. No Liability — User Files and Folder Structures

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.

**SustainableX and its contributors SHALL NOT BE LIABLE for:**
- Loss, corruption, or unintended modification of user files or folder structures
- Data loss resulting from document indexing, vector embedding, or processing
- Inaccuracies, errors, or omissions in AI-generated reports or analyses
- Business decisions made based on AI-generated content
- Regulatory non-compliance resulting from use of generated reports
- Any direct, indirect, incidental, special, or consequential damages

## 2. Access Restrictions

ai4sustainablex only accesses folders **explicitly specified by the user** during setup or via CLI commands. It will not scan, read, process, or index files outside the designated directory. You control exactly which folders are indexed.

## 3. Local Processing

All document processing, text extraction, vector embedding generation, and LLM inference (when using Ollama) occurs **entirely on your local machine**. No data is uploaded to any cloud service unless you explicitly configure cloud-based providers (OpenAI, Anthropic, DeepSeek, Google Gemini, Kimi).

## 4. Third-Party Services

When using cloud-based LLM providers, your queries and retrieved context are transmitted to their respective API endpoints. You are responsible for reviewing and agreeing to their individual privacy policies and terms of service:
- OpenAI: https://openai.com/policies
- Anthropic: https://www.anthropic.com/legal
- DeepSeek: https://deepseek.com/terms
- Google Gemini: https://ai.google.dev/terms
- Kimi/Moonshot: https://www.moonshot.cn/privacy

## 5. API Key Security

API keys are stored locally in `~/.ai4sustainablex/config.json` and are **never transmitted** except to authenticate with the respective service endpoints that you have configured.

## 6. Report Accuracy & Professional Review

**ai4sustainablex is an assistive tool, NOT a substitute for professional ESG consulting.**

Generated reports combine automatically retrieved documents with AI-generated content. Retrieval-Augmented Generation (RAG) can produce inaccurate or incomplete results. ALL AI-generated reports should be reviewed, verified, and approved by a qualified ESG, sustainability, or compliance professional before any external use or regulatory submission.

## 7. Template Accuracy

Report templates provide structural guidance and prompts for ESG frameworks. They are provided as-is and may not reflect the most current versions of reporting standards. Users are responsible for verifying template alignment with the latest framework requirements from:
- GRI (Global Reporting Initiative)
- SBTi (Science Based Targets initiative)
- CDP (Carbon Disclosure Project)
- IFRS Foundation (ISSB Standards)
- EFRAG (European Sustainability Reporting Standards)
- SEBI (Business Responsibility and Sustainability Reporting)

## 8. Intellectual Property

ai4sustainablex source code is licensed under the Business Source License 1.1 (BUSL-1.1) — free for personal, internal research, and internal corporate ESG reporting — converting to Apache License 2.0 on July 25, 2030. SustainableX retains all rights to the name "ai4sustainablex", branding assets, the SustainableX website (sustainablex.in), the Template Library, and the Validation service accessible via the SustainableX API.

## 9. Data Privacy

- No telemetry, analytics, or usage data is collected or transmitted
- No user documents or indexed content are ever sent to SustainableX servers
- No account or registration is required
- The software does not include any tracking, advertising, or analytics SDKs

## 10. Governing Law & Jurisdiction

These terms are governed by the laws of India. Any disputes arising from the use of this software shall be subject to the exclusive jurisdiction of courts in Mumbai, Maharashtra.

## 11. Acceptance

By installing or using ai4sustainablex, you acknowledge that you have read, understood, and agree to be bound by these terms. If you do not agree, do not install or use the software.

---

**Last Updated**: 25 July 2026  
**Contact**: info@sustainablex.in  
**Website**: https://sustainablex.in