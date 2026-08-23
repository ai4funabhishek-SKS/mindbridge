# Project Rules: [Your Project Name Here]

## 1. Project Vision & Goal
*   **Primary Goal:** [e.g., To create a simple, beautiful website for my local bakery that showcases products and allows customers to place pickup orders.]
*   **Target Audience:** [e.g., Local customers aged 25-55, primarily using mobile phones.]
*   **Success Metrics:** [e.g., Launch the MVP within 2 weeks, achieve a Google Lighthouse performance score above 90.]

## 2. Technical Stack & Requirements
*   **Front-end:** [e.g., HTML, CSS, vanilla JavaScript. Keep it simple and framework-free for easy maintenance.]
*   **Back-end & Database:** [e.g., Use a free BaaS (Backend-as-a-Service) like Supabase.]
*   **Hosting:** [e.g., Deploy to a free platform like Netlify or Vercel.]
*   **Key Requirement:** The website must be fully responsive (mobile-first).

## 3. Dependency, API, & Tool Management
*   **Proactive Checks & Instructions:** Before writing code that requires a new external library, API, or service, you MUST:
    1.  **Identify:** Clearly state which dependency is about to be used and why it is necessary.
    2.  **Check:** Verify if this dependency is free, its cost structure, and any account requirements.
    3.  **Guide:** Provide a detailed, step-by-step instruction list for me to obtain and configure it (e.g., for an API: "1. Go to [website.com/api]. 2. Click 'Sign Up'. 3. Go to the 'Dashboard' section. 4. Click 'Create New API Key'. 5. Copy the key."). If an official tutorial exists, provide the direct link.
*   **MCP Server Protocol:** If a task would be significantly enhanced by using a Model Context Protocol (MCP) server (e.g., for specialized code execution, database browsing, or design generation), you must:
    1.  **Assess & Request:** Clearly explain what an MCP server is in simple terms and justify why it is needed for this specific use case.
    2.  **Specify:** Name the specific MCP server required (e.g., "I need access to the `sqlite` MCP server to browse and manage your database directly").
    3.  **Guide:** Provide clear, simple instructions on how I can enable it for our session if I approve.
*   **Principle:** Prefer simpler solutions with fewer dependencies to avoid bloat and complexity.

## 4. User Action Required
*   **Advance Notice:** Any task that requires action from my end (e.g., signing up for a service, obtaining an API key, installing a local tool) must be identified as far in advance as possible.
*   **Structured Instructions:** Instructions must be provided in a numbered list, written in clear, simple English, and include:
    *   **Website Links:** Direct URLs to the exact page I need to visit.
    *   **What to Click:** Specific button names and menu paths.
    *   **What to Copy:** Clearly identify what information I need to copy and save (e.g., "Copy the API Key string, it will look like `sk_1a2b3c...`").
    *   **Where to Paste:** Explain where in our project this information will need to be used later.

## 5. Testing Strategy
*   **Testing Framework:** For this project, we will use [e.g., Manual testing instructions. If complexity grows, recommend a framework like Jest or Cypress.].
*   **Testing Requirements:** For every major feature, you must provide:
    *   **How to Test:** Simple, step-by-step instructions on how to manually test the feature (e.g., "1. Click the button. 2. A green success message should appear.").
    *   **What to Test:** A checklist of key user actions and edge cases (e.g., "Test what happens if the user submits the form without an email.").
*   **Goal:** Ensure every feature is verified to work as intended before we consider it complete.

## 6. Industry Best Practices for This Project
You must adhere to and explain the following best practices relevant to our tech stack:
*   **Performance:** Optimize images, use efficient code, and leverage browser caching for fast loading times.
*   **Security:** Never hardcode API keys, passwords, or sensitive data. Use environment variables. All user data must be validated and sanitized.
*   **Accessibility (a11y):** Use semantic HTML tags (like `<header>`, `<nav>`, `<button>`), provide alt text for images, and ensure good color contrast so the site is usable for everyone.
*   **Maintainability:** Write clean, well-commented code. Keep structure logical (e.g., separate folders for images, CSS, and JavaScript files).

## 7. Core Features (Minimum Viable Product - MVP)
List the essential features for the first version:
1.  [e.g., Homepage with hero image and call-to-action]
2.  [e.g., Menu page with categories]
3.  [e.g., A simple contact form]
4.  [e.g., A 'Order for Pickup' system (basic cart and checkout)]

## 8. Deployment & Maintenance
*   **Deployment Process:** Provide a clear, step-by-step guide to deploy the final site to our chosen hosting platform.
*   **Post-Launch Checklist:** Include a list of tasks to do after launch (e.g., submit sitemap to Google Search Console, connect a custom domain).
*   **Maintenance Advice:** Advise on how to update content (e.g., adding a new menu item) and how to monitor the site's health.

---

*This document serves as the single source of truth for the project's direction. Any changes to these rules should be discussed and updated here.*