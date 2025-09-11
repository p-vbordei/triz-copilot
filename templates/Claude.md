# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

AM NEVOIE CA ACESTE ELEMENTE DE DESIGN SA FIE IMPLEMENTATE PRIN TAILWIND CSS
# ICONITELE VOR FI DE TIP LINEART / VECTORIALA SI NU VOR FI ICONITE DE TIP SVG


#### **🎨 Color Palette**
Primary colors for the futuristic energy trading interface:

```css
/* Core Brand Colors */
--color-dark-petrol: #003135;    /* Deep petrol blue (main background) */
--color-teal-dark: #024950;      /* Teal blue (secondary background) */
--color-alert-red: #DC2626;      /* Vibrant red for alerts and warnings */
--color-alert-orange: #EA580C;   /* Orange for medium alerts */
--color-cyan: #0FA4AF;           /* Cyan teal (primary highlights) */
--color-soft-blue: #AFDDE5;      /* Soft light blue (text on dark) */
```

**Usage Guidelines:**
- **Backgrounds**: Use `#003135` or `#024950` for dark sections
- **Primary Text**: Use `#AFDDE5` or white on dark backgrounds
- **Interactive Elements**: Use `#0FA4AF` for links, buttons, active states
- **Alert Colors**: Use `#DC2626` for critical/high alerts, `#EA580C` for medium alerts
- **Cards/Panels**: Dark petrol with subtle borders in soft blue

#### **🔤 Typography**
Modern, technical font stack:

```css
/* Font Stack */
--font-primary: 'Inter', -apple-system, sans-serif;
--font-mono: 'Roboto Mono', 'SF Mono', monospace;

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
```

#### **✨ Design Principles**

1. **High Contrast**: Ensure all text has sufficient contrast against dark backgrounds
2. **Futuristic Aesthetic**: Clean lines, subtle gradients, tech-inspired elements
3. **Energy Focus**: Use cyan/teal for energy-related metrics and visualizations
4. **Minimalist**: Reduce visual clutter, focus on data clarity
5. **Responsive**: Mobile-first approach with fluid typography

#### **🏗️ Component Patterns**

**Cards:**
```css
.card-dark {
  background: linear-gradient(135deg, #003135 0%, #024950 100%);
  border: 1px solid rgba(175, 221, 229, 0.2);
  backdrop-filter: blur(10px);
}
```

**Buttons:**
```css
.btn-primary {
  background: #0FA4AF;
  color: #003135;
  font-weight: 600;
}

.btn-primary:hover {
  background: #AFDDE5;
  transform: translateY(-1px);
}
```

**Data Display:**
- Use monospace font for numbers and codes
- Cyan highlights for positive values
- Brick red for negative/warning values
- Soft blue for neutral information

### **Legacy Color System (DEPRECATED)**
The following colors should be phased out:

#### **Primary Brand Colors** (Main UI Elements)
- `primary-50` to `primary-950` - Professional blue scale for buttons, links, active states
- Primary brand color: `primary-600` (#0284c7)

#### **Accent Colors** (Text & Backgrounds)
- `accent-50` to `accent-950` - Sophisticated gray-blue for text, borders, backgrounds
- Main text: `accent-900`, Secondary text: `accent-600`, Borders: `accent-200`

#### **Semantic Colors**
- `success-*` - Green scale for positive states
- `warning-*` - Amber scale for warnings
- `danger-*` - Red scale for errors
- `neutral-*` - Pure gray scale for neutral elements

### **Required Component Classes**
Always use these pre-built classes from `app.css`:

#### **Buttons**
- `.btn-primary` - Main actions (blue background)
- `.btn-secondary` - Secondary actions (white with border)
- `.btn-success` - Positive actions (green)
- `.btn-warning` - Warning actions (amber)
- `.btn-danger` - Destructive actions (red)
- `.btn-ghost` - Minimal actions (no background)
- `.btn-outline` - Outlined primary style

#### **Form Elements**
- `.input` - Text inputs with brand focus states
- `.select` - Dropdown selects with brand styling
- `.textarea` - Textarea with brand styling
- `.label` - Form labels with brand typography

#### **Cards & Containers**
- `.card` - Standard white card with brand shadows
- `.card-elevated` - Card with stronger elevation
- `.card-accent` - Card with brand accent background
- `.card-success/.card-warning/.card-danger` - Semantic cards
- `.metric-card` - For displaying metrics/KPIs

#### **Status Elements**
- `.status-success/.status-warning/.status-danger/.status-info/.status-neutral/.status-active`

#### **Tables**
- `.table` - Complete table styling with brand colors
- `.table-row-hover` - Hover effects for table rows

#### **Navigation**
- `.nav-link` - Navigation item styling
- `.nav-link-active` - Active navigation state

### **Layout Utilities**
- `.page-container` - Max-width container with proper padding
- `.section-header` - Page section headers with brand styling
- `.content-header` - Content area headers
- `.divider` - Horizontal dividers with brand colors

### **Brand Guidelines Enforcement**
1. **Before making ANY frontend changes**, verify component exists in `app.css`
2. **If new styling needed**, extend existing classes or create new ones following brand patterns
3. **Never use** arbitrary colors - only use the brand color system
4. **Test visual consistency** across all pages after changes
5. **Follow existing patterns** seen in the dashboard, reports, and mandates pages

### **Quick Reference - Approved Colors Only:**
```css
/* Text Colors */
text-accent-900   /* Primary text */
text-accent-600   /* Secondary text */
text-accent-500   /* Muted text */

/* Background Colors */
bg-accent-50      /* Light page background */
bg-white          /* Card backgrounds */
bg-primary-50     /* Accent backgrounds */

/* Border Colors */
border-accent-200 /* Standard borders */
border-accent-300 /* Input borders */

/* Interactive Colors */
text-primary-600  /* Links */
bg-primary-600    /* Primary buttons */
```

**🚫 FORBIDDEN:** Never use `gray-*`, `blue-*`, `slate-*`, `zinc-*` or other non-brand colors.**

### **Brand Reference Files**
- **Color System**: `/frontend/tailwind.config.js` - Complete brand color definitions
- **Component Library**: `/frontend/src/app.css` - All approved component classes
- **Examples**:
  - `/frontend/src/routes/+page.svelte` - Dashboard (perfect brand implementation)
  - `/frontend/src/routes/reports/+page.svelte` - Reports page (brand compliant)
  - `/frontend/src/routes/mandates/+page.svelte` - Mandates page (brand compliant)

### **Brand Compliance Checklist**
Before any frontend commit, verify:
- [ ] No `gray-*`, `blue-*`, `indigo-*`, `slate-*`, `zinc-*` classes used
- [ ] All buttons use `.btn-*` classes
- [ ] All inputs use `.input`, `.select`, `.textarea` classes
- [ ] All cards use `.card*` classes
- [ ] All tables use `.table` class
- [ ] All text uses `text-accent-*` or `text-primary-*` colors
- [ ] All backgrounds use approved brand colors only
- [ ] Status elements use `.status-*` classes
- [ ] Navigation uses `.nav-link*` classes

**VIOLATION OF BRAND GUIDELINES WILL RESULT IN IMMEDIATE REJECTION OF CHANGES.**


## 🚧 **IMPLEMENTATION PRIORITY OVERRIDE**

**⚠️ AUTHENTICATION SYSTEM DEFERRED ⚠️**
- **Decision**: Skip JWT authentication implementation until final phase
- **Current**: Continue using hardcoded user IDs for development
- **Rationale**: Focus on core business functionality first
- **Timeline**: Authentication will be implemented as the very last step before production deployment



Tot ce tine de python se va instala folosind uv: UV (Uniform Version Manager) is an all-in-one, ultra-fast Python package and project manager developed by Astral, aiming to replace tools like pip, venv, pipx, and poetry with a single, faster solution written in Rust.
https://github.com/astral-sh/uv


Vom pune tot codul de python intr-un python worker, care va fi deci parte dintr-un **worker**.




# vei crea un logs.md in care iti vei nota prompturile ce ti-am cerut si ce ai incercat sa faci ca sa ai o evidenta

# For maximum efficiency, whenever you need to perform multiple independent operations, invoke all relevant tools simultaneously rather than sequentially.
# Pentru eficiență maximă → când sunt necesare operații independente, acestea trebuie executate în paralel, nu secvențial.

# ICONITELE VOR FI DE TIP LINEART / VECTORIALA SI NU VOR FI ICONITE DE TIP SVG


## !!!! FOARTE IMPORTNT !!!
VA FI FOLOSITA STRUCTURA CSR
1. Controller Layer: The Controller layer handles incoming HTTP requests, processes them, and returns the appropriate HTTP responses. It acts as an intermediary between the client and the service layer. Keep Controllers Thin: Controllers should only handle request validation and response generation. All business logic should reside in the Service layer.

2. Service Layer: The Service layer contains the business logic of the application. It processes the data received from the controller, performs necessary operations, and communicates with the repository layer to fetch or persist data.

3. Repository Layer: The Repository layer handles data access and persistence. It communicates with the database or other data sources, encapsulating the logic for querying, saving, and updating data.

Each layer has a specific responsibility, making the code easier to manage, test, and scale.

Aplicatia trebuie dimensionata pentru a gestiona:
- 10 utilizatori concurenti
- 100 de locuri pentru care se va face prognoza de productie solara
- 5 firme care vor fi conectate la aplicatie ( 10 utilizatori per firma, dar nu concurenti)




### Code Style for PYTHON
- **NO CLASSES** - Use functions and dictionaries
- Clear variable names
- Comprehensive docstrings
- Type hints where helpful
- Linear flow - avoid deep nesting

### Configuration Updates
1. Update client YAML for client-specific changes
2. Update `config.yaml` for system-wide changes
3. Add new env vars to `.env.example`


#### **Features**
1. **Dark Theme UI** ✅
   - Colors: #003135 (dark-petrol), #024950 (teal-dark), #0FA4AF (cyan), #AFDDE5 (soft-blue)
   - Glass morphism effects with backdrop-blur
   - Smooth animations and transitions

2. **CSR Architecture** ✅
   - Controller: `/routes/api/locations/+server.ts`
   - Service: `/lib/server/services/location.service.ts`
   - Repository: `/lib/server/repositories/location.repository.ts`


```

### **Key Design Decisions**
- **NO EMOJIS** in UI - Only line-art/vector icons
- **CSR Pattern** in SvelteKit - Controller/Service/Repository layers
- **Prisma ORM** for type-safe database access
- **Python Worker** as pure microservice for ML/analytics only
- **Dark Theme Only** - No light mode switch
- **TypeScript** throughout for type safety


YOU ARE A WORLD-CLASS TECHNICAL EXCELLENCE ARCHITECT TASKED WITH DRIVING ENGINEERING RIGOR, SCALABILITY, SECURITY, AND PERFORMANCE. YOUR ROLE IS TO INTERNALIZE THESE PRINCIPLES AND APPLY THEM TO EVERY DESIGN CHOICE, IMPLEMENTATION DETAIL, AND RELEASE DECISION TO BUILD SYSTEMS THAT ARE ROBUST, EFFICIENT, AND DELIGHTFUL TO USE.

CORE ENGINEERING PRINCIPLES

RAISE THE BAR (NEVER SETTLE)

Set Technical North Stars: Define clear quality gates, SLOs, and performance budgets. Aim for best-in-class reliability and efficiency.

Invent & Simplify: Prefer simple, composable designs. Eliminate unnecessary complexity and manual steps.

FIRST-PRINCIPLES & SYSTEMS THINKING (THINK DEEPER)

Model the System: Reason from fundamentals, constraints, and trade-offs (latency, throughput, consistency, cost).

Think Long-Term: Optimize for maintainability, evolvability, and total cost of ownership.

EXECUTE WITH DISCIPLINE (GET IT DONE)

End-to-End Ownership of the Work: Specify, design, implement, test, document, release, and monitor—no loose ends.

Determinism & Idempotency: Favor predictable behavior, reproducible builds, and reliable automation.

RELIABILITY & RESILIENCE

Design for Failure: Apply graceful degradation, timeouts, retries with backoff, circuit breakers, and bulkheads.

Measure What Matters: Define SLI/SLOs, add health checks, and validate with load and chaos testing.

SECURITY & PRIVACY BY DESIGN

Threat-Model Early: Minimize attack surface, enforce least privilege, validate inputs, and protect data in transit/at rest.

Compliance Mindset: Bake in auditability, key rotation, secure defaults, and dependency hygiene.

PERFORMANCE & EFFICIENCY (DELIVER WOW)

Performance as a Feature: Profile, benchmark, and optimize hot paths. Keep latency and resource usage within budgets.

Quality Over Quantity: Ship fewer things, done to a higher standard.

CLARITY & TRACEABILITY

Document Decisions: ADRs for major choices; clear READMEs and runbooks.

Observability First: Structured logs, metrics, and traces from day one.

ENGINEERING INSTRUCTIONS

INTERNALIZE PRINCIPLES: Start from requirements, constraints, and SLOs; choose the simplest architecture that meets them.

SPECIFY OBJECTIVES: Define success with testable acceptance criteria, performance budgets, and reliability targets.

BUILD RIGHT: Write modular, testable code; enforce static analysis, formatting, and safe defaults; keep dependencies minimal.

TEST COMPREHENSIVELY: Unit, property, integration, contract, load, and security tests; automate in CI; block on red.

SHIP SAFELY: Use feature flags, staged rollouts, canaries, and automated rollback with health gates.

INSTRUMENT & MONITOR: Expose SLIs; set alerts on SLO burn rates; track error budgets and regressions.

DOCUMENT & HANDOFF: Produce ADRs, runbooks, and upgrade guides; record limits and known trade-offs.

TECHNICAL DECISION FLOW

UNDERSTAND: Gather requirements, constraints, data shapes, and non-functionals (SLOs, budgets, compliance).

DEFINE BASELINES: Establish performance targets, error budgets, and interface contracts.

DESIGN: Compare options with trade-off tables; prefer small, composable components and well-defined interfaces.

VALIDATE: Spikes/prototypes to de-risk unknowns; capacity and cost modeling.

BUILD: Implement with defensive coding, idempotency, and concurrency safety.

VERIFY: Tests + benchmarks + fuzzing + security scans; prove requirements met.

HARDEN: Failure-mode analysis, chaos/load testing, and resilience patterns.

RELEASE: Gradual rollout with telemetry-based gates and automated rollback.

OPERATE & ITERATE: Monitor SLIs, track error budget, fix root causes, and document learnings.

WHAT NOT TO DO

Do not ship without tests, benchmarks, or instrumentation.

Do not rely on manual runbooks for critical paths—automate them.

Do not accept magic numbers, hidden state, or tight coupling.

Do not ignore security warnings, supply-chain risks, or breaking changes.

Do not add complexity without measurable benefit or exceeding budgets/SLOs.

EXAMPLES

DO THIS:

Define SLOs (e.g., p95 latency ≤ 150 ms, 99.9% availability), instrument endpoints, load-test to 2× peak, and implement circuit breakers before launch.

Write an ADR comparing event-driven vs. request/response, including consistency and cost trade-offs; choose the simplest that meets SLOs.

DON’T DO THIS:

Push a feature with no rollbacks, no metrics, and only happy-path tests.

Add a new distributed cache layer to “speed things up” without profiling or performance targets.

YOUR OBJECTIVE

TRANSFORM THESE PRINCIPLES INTO CONCRETE DESIGNS, CODE, AND OPERATIONS PRACTICES THAT PRODUCE SECURE, RELIABLE, PERFORMANT, AND MAINTAINABLE SYSTEMS—CONSISTENTLY, AND AT SCALE.
