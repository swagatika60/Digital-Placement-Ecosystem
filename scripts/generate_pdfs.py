#!/usr/bin/env python3
"""
Generate text-based placement-preparation PDFs into app/static/pdfs/.

Uses only the Python standard library (no reportlab / fpdf dependency).
Lines beginning with "#" are rendered as bold headings.

Usage:
    python scripts/generate_pdfs.py
"""
import os

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "app", "static", "pdfs",
)

PAGE_W, PAGE_H = 612, 792
MARGIN = 54
BODY_SIZE = 11
HEADING_SIZE = 14
LINE_H = 15


def _escape(text):
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def build_pdf(title, lines):
    """Return bytes of a valid minimal PDF with one or more text pages.

    Object layout:
      1            -> Catalog
      2            -> Pages (kids)
      3,4,5,6...   -> page, its content stream, page, stream, ...
      last two     -> Helvetica, Helvetica-Bold fonts
    """
    # split lines into pages
    usable = PAGE_H - 2 * MARGIN
    per_page = max(1, int(usable // LINE_H))
    chunks = [lines[i:i + per_page] for i in range(0, len(lines), per_page)] or [[]]
    n_pages = len(chunks)

    font_helv = 3 + 2 * n_pages       # Helvetica
    font_bold = font_helv + 1         # Helvetica-Bold

    objects = []          # list of (object_number, body_bytes)
    kids = []

    for chunk in chunks:
        page_num = 3 + 2 * len(kids)
        content_num = page_num + 1
        kids.append(f"{page_num} 0 R")

        # content stream for this page
        stream_parts = ["BT"]
        y = PAGE_H - MARGIN - BODY_SIZE
        for line in chunk:
            if not line.strip():
                y -= LINE_H
                continue
            if line.startswith("#"):
                font, size = font_bold, HEADING_SIZE
                text = line[1:].strip()
            else:
                font, size = font_helv, BODY_SIZE
                text = line
            stream_parts.append(
                f"/F{font} {size} Tf 1 0 0 1 54 {y} Tm ({_escape(text)}) Tj"
            )
            y -= LINE_H
        stream_parts.append("ET")
        stream = "\n".join(stream_parts).encode("latin-1")

        objects.append((page_num, (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
            f"/Contents {content_num} 0 R "
            f"/Resources << /Font << /F{font_helv} {font_helv} 0 R "
            f"/F{font_bold} {font_bold} 0 R >> >> >>"
        ).encode("latin-1")))

        stream_obj = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1")
            + stream
            + b"\nendstream"
        )
        objects.append((content_num, stream_obj))

    objects.append((1, b"<< /Type /Catalog /Pages 2 0 R >>"))
    objects.append((2, (
        f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {n_pages} >>"
    ).encode("latin-1")))
    objects.append((font_helv, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"))
    objects.append((font_bold, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"))
    objects.sort(key=lambda item: item[0])

    out = bytearray(b"%PDF-1.4\n")
    offsets = {}
    for num, body in objects:
        offsets[num] = len(out)
        out += f"{num} 0 obj\n".encode("latin-1")
        out += body
        out += b"\nendobj\n"

    xref_pos = len(out)
    count = len(objects) + 1
    out += f"xref\n0 {count}\n".encode("latin-1")
    out += b"0000000000 65535 f \n"
    for num, _ in objects:
        out += f"{offsets[num]:010d} 00000 n \n".encode("latin-1")

    out += (
        f"trailer\n<< /Size {count} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"
    ).encode("latin-1")
    return bytes(out)


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------

PDFS = {
    "os_notes.pdf": [
        "# Operating Systems - Quick Interview Notes",
        "Processes, Threads, Memory, Scheduling",
        "",
        "# 1. Process vs Thread",
        "- Process: independent program in execution with its own memory space.",
        "- Thread: lightweight unit of execution inside a process, shares memory.",
        "- Context switch between threads is cheaper than between processes.",
        "",
        "# 2. Process States",
        "- New -> Ready -> Running -> Blocked/Waiting -> Terminated.",
        "- Only one process runs on a single CPU core at a time.",
        "",
        "# 3. CPU Scheduling Algorithms",
        "- FCFS: First Come First Served (simple, convoy effect).",
        "- SJF: Shortest Job First (min avg waiting, needs burst time).",
        "- Round Robin: time slices, good for interactive systems.",
        "- Priority Scheduling: can starve low-priority processes.",
        "- MLFQ: Multiple Level Feedback Queues (used in modern OS).",
        "",
        "# 4. Deadlock - 4 Necessary Conditions",
        "- Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait.",
        "- Avoid via Banker Algorithm (safe state), prevent by breaking one condition.",
        "",
        "# 5. Memory Management",
        "- Paging: fixed-size pages/frames, no external fragmentation.",
        "- Segmentation: variable-size segments, external fragmentation possible.",
        "- Page replacement: FIFO, LRU, Optimal, Clock (Second Chance).",
        "- Thrashing: excessive paging due to too many active pages.",
        "",
        "# 6. Virtual Memory",
        "- Allows programs larger than physical RAM using demand paging.",
        "- TLB (Translation Lookaside Buffer) caches page-table entries.",
        "",
        "# 7. Inter-Process Communication (IPC)",
        "- Shared Memory and Message Passing.",
        "- Pipes (unidirectional), message queues, semaphores, sockets.",
        "",
        "# 8. Common Interview Topics",
        "- Semaphores vs Mutex: counting vs binary lock.",
        "- Starvation, Race condition, Critical Section problem.",
        "- Zombie (child done, not reaped) vs Orphan (parent died) process.",
    ],
    "networking_notes.pdf": [
        "# Computer Networking - Quick Interview Notes",
        "OSI Model, TCP/IP, Protocols",
        "",
        "# 1. OSI 7 Layers (top to bottom)",
        "- 7 Application, 6 Presentation, 5 Session, 4 Transport,",
        "- 3 Network, 2 Data Link, 1 Physical.",
        "- Mnemonic: All People Seem To Need Data Processing.",
        "",
        "# 2. TCP/IP Model (4 layers)",
        "- Application, Transport, Internet, Network Access.",
        "- HTTP, FTP, SMTP, DNS live at Application layer.",
        "",
        "# 3. TCP vs UDP",
        "- TCP: connection-oriented, reliable, ordered, flow control.",
        "- UDP: connectionless, fast, no guarantees (video, DNS).",
        "- 3-way handshake: SYN, SYN-ACK, ACK.",
        "",
        "# 4. Important Protocols",
        "- HTTP/HTTPS: web (HTTPS = TLS encryption).",
        "- DNS: resolves domain names to IP addresses (port 53).",
        "- DHCP: auto-assigns IP addresses (port 67/68).",
        "- SMTP: sending mail (25/587). IMAP/POP3: receiving mail.",
        "- FTP/SFTP: file transfer. SSH: secure remote shell (22).",
        "",
        "# 5. IP Addressing",
        "- IPv4: 32-bit, e.g. 192.168.1.1 (private range).",
        "- IPv6: 128-bit, solves address exhaustion.",
        "- Subnet mask divides network and host portions.",
        "- NAT: maps private IPs to one public IP.",
        "",
        "# 6. HTTP Basics",
        "- Status codes: 200 OK, 301/302 redirect, 401/403 auth,",
        "- 404 Not Found, 500 Internal Server Error.",
        "- GET vs POST: idempotent retrieval vs state-changing submit.",
        "- Cookies vs Sessions: client-side storage vs server-side state.",
        "",
        "# 7. Common Interview Questions",
        "- Difference between Hub, Switch, Router.",
        "- What happens when you type a URL? (DNS -> TCP -> HTTP -> render).",
        "- Load balancer: distributes traffic (round robin, least connections).",
    ],
    "python_notes.pdf": [
        "# Python Interview Guide",
        "Fundamentals, Data Structures, OOP, Tricky Questions",
        "",
        "# 1. Core Concepts",
        "- Python is dynamically typed and interpreted (bytecode via CPython).",
        "- GIL (Global Interpreter Lock) limits true multi-threading for CPU work.",
        "- Lists vs Tuples: mutable vs immutable.",
        "- Sets: unordered, unique. Dicts: key-value, insertion-ordered (3.7+).",
        "",
        "# 2. Common Built-ins",
        "- len(), range(), enumerate(), zip(), map(), filter(), sorted().",
        "- Lambda: anonymous single-expression function.",
        "- List comprehension: [x*2 for x in range(10) if x % 2 == 0].",
        "",
        "# 3. OOP in Python",
        "- Class vs Instance vs Static methods (@classmethod, @staticmethod).",
        "- __init__ constructor, __str__ / __repr__ for display.",
        "- Inheritance, Method Resolution Order (MRO), super().",
        "- Multiple inheritance supported (unlike Java).",
        "",
        "# 4. Decorators & Generators",
        "- Decorator: function that wraps another function.",
        "- Generator: yields values lazily using yield; memory efficient.",
        "",
        "# 5. Error Handling",
        "- try / except / else / finally blocks.",
        "- Custom exceptions subclass Exception.",
        "",
        "# 6. Memory & Performance",
        "- Shallow vs deep copy (copy.copy vs copy.deepcopy).",
        "- == compares values, is compares identity.",
        "- String immutability: joining with join() is faster than +=.",
        "",
        "# 7. Tricky Interview Questions",
        "- Output of [1,2,3]*2 -> [1,2,3,1,2,3].",
        "- Default mutable argument pitfall (use None instead of []).",
        "- Difference between remove, pop, and del on lists.",
        "- Global vs nonlocal keyword.",
    ],
    "system_design_notes.pdf": [
        "# System Design Primer",
        "Scalability, Caching, Databases, Load Balancing",
        "",
        "# 1. Scalability Basics",
        "- Vertical scaling: bigger machine (limited, single point of failure).",
        "- Horizontal scaling: more machines behind a load balancer.",
        "",
        "# 2. Load Balancing",
        "- Algorithms: Round Robin, Least Connections, IP Hash.",
        "- L4 (transport) vs L7 (application) load balancers.",
        "",
        "# 3. Caching",
        "- Cache-aside, Write-through, Write-back strategies.",
        "- Redis/Memcached for in-memory caching.",
        "- Cache eviction: LRU (least recently used), TTL.",
        "",
        "# 4. Databases",
        "- SQL vs NoSQL: structured/ACID vs flexible/schema-less.",
        "- Indexes speed up reads, slow down writes.",
        "- Sharding: horizontal partition of data by key.",
        "- Replication: master-slave, leaderless.",
        "- CAP theorem: pick 2 of Consistency, Availability, Partition tolerance.",
        "",
        "# 5. Messaging & Async",
        "- Queues decouple services (RabbitMQ, Kafka, SQS).",
        "- Event-driven vs request-response architecture.",
        "",
        "# 6. Key Interview Flow",
        "- Clarify requirements -> estimate scale -> high-level design",
        "- -> dive into components -> discuss trade-offs.",
        "- Always consider: caching, load, DB choice, failure modes.",
    ],
    "amazon_interview_guide.pdf": [
        "# Amazon Interview Guide",
        "Leadership Principles, Rounds, Preparation Tips",
        "",
        "# 1. Interview Rounds",
        "- Online Assessment (OA): 2-3 coding problems.",
        "- Phone screen: 1 coding round.",
        "- Onsite: 3-4 technical + 1 Bar Raiser (leadership principles).",
        "",
        "# 2. Key Leadership Principles to Prepare",
        "- Customer Obsession, Ownership, Invent and Simplify.",
        "- Are Right, A Lot; Learn and Be Curious; Hire and Develop the Best.",
        "- Insist on the Highest Standards; Think Big; Bias for Action.",
        "- Frugality, Earn Trust, Dive Deep, Have Backbone, Deliver Results.",
        "",
        "# 3. Coding Preparation",
        "- Arrays, Strings, HashMaps, Trees, Graphs, DP.",
        "- Practice on LeetCode (Easy/Medium/Hard mix).",
        "- Explain approach + complexity before coding (think out loud).",
        "- Optimize brute force to an efficient solution.",
        "",
        "# 4. Behavioral (STAR) Tips",
        "- Situation, Task, Action, Result for every story.",
        "- Use metrics: improved X% / reduced Y ms / served Z users.",
        "- Bar Raiser: be specific and take ownership in answers.",
        "",
        "# 5. System Design (SDE II+)",
        "- Design a shopping cart, recommendation feed, rate limiter.",
        "- Cover load estimation, APIs, data model, caching, scaling.",
    ],
    "google_interview_guide.pdf": [
        "# Google Interview Guide",
        "Process, Rounds, and Preparation Strategy",
        "",
        "# 1. Interview Rounds",
        "- Coding interviews (2-4): algorithms and data structures.",
        "- Googleyness / leadership round: behavioral.",
        "- Role-specific: system design or domain knowledge.",
        "",
        "# 2. Coding Round Focus",
        "- Strong fundamentals: arrays, strings, hash tables, trees, graphs.",
        "- Dynamic programming and recursion appear frequently.",
        "- Write clean, correct code with edge cases handled.",
        "- Discuss time and space complexity clearly.",
        "",
        "# 3. Problem-Solving Approach",
        "- Restate the problem and ask clarifying questions.",
        "- Start with a brute-force solution, then optimize.",
        "- Test with small examples and edge cases.",
        "- Communicate constantly while coding.",
        "",
        "# 4. Googleyness / Behavioral",
        "- Questions about collaboration, ambiguity, and leadership.",
        "- Use STAR format with measurable impact.",
        "- Show humility, curiosity, and a bias to action.",
        "",
        "# 5. System Design (for senior roles)",
        "- Practice designing scalable systems (search, maps, video).",
        "- Know trade-offs between different approaches.",
    ],
    "microsoft_interview_guide.pdf": [
        "# Microsoft Interview Guide",
        "Rounds, Culture, and Preparation Tips",
        "",
        "# 1. Interview Rounds",
        "- Screening: coding + behavioral.",
        "- Loop: 4-5 rounds (coding, system design, culture fit).",
        "- ASK (Aptitude, Skills, Knowledge) manager round at the end.",
        "",
        "# 2. Coding Preparation",
        "- Focus on arrays, strings, linked lists, trees, recursion.",
        "- C#, Java, or Python are all acceptable.",
        "- Write production-quality code: naming, structure, tests.",
        "- Consider edge cases and complexity trade-offs.",
        "",
        "# 3. Microsoft Culture - Growth Mindset",
        "- Emphasize learning from failures and feedback.",
        "- One Microsoft: collaboration across teams.",
        "- Customer obsession and accessibility in design.",
        "",
        "# 4. Behavioral Questions",
        "- Why Microsoft? (research products and mission).",
        "- Tell me about a conflict and how you resolved it.",
        "- Describe a project where you took initiative.",
        "",
        "# 5. System Design",
        "- Design a cloud service, chat application, or distributed cache.",
        "- Know Azure fundamentals: VMs, Blob Storage, Functions, AKS.",
    ],
    "tcs_nqt_guide.pdf": [
        "# TCS NQT Preparation Guide",
        "Test Pattern and Section-Wise Strategy",
        "",
        "# 1. Test Pattern (NQT)",
        "- Numerical Ability: 20 Qs, aptitude, percentages, ratios.",
        "- Reasoning Ability: puzzles, series, coding-decoding.",
        "- Verbal Ability: grammar, reading comprehension.",
        "- Programming Logic (pseudo-code based).",
        "- Optional: Coding round (2 problems).",
        "",
        "# 2. Numerical Ability Tips",
        "- Master percentages, profit-loss, time-work, speed-distance.",
        "- Learn shortcut methods for average and ratio problems.",
        "- Practice 10-15 questions daily with a timer.",
        "",
        "# 3. Reasoning Tips",
        "- Number/letter series, analogies, syllogisms.",
        "- Blood relations, directions, seating arrangement.",
        "",
        "# 4. Verbal Tips",
        "- Vocabulary (synonyms, antonyms), sentence correction.",
        "- Read one editorial daily for RC speed.",
        "",
        "# 5. Programming Logic",
        "- Understand C/Java/Python code snippets (output, errors).",
        "- Know loops, conditionals, arrays, basic OOP.",
        "- Practice pseudo-code MCQs from previous papers.",
        "",
        "# 6. General Advice",
        "- No negative marking in most sections.",
        "- Attempt all questions; manage time per section.",
    ],
    "infosys_interview_guide.pdf": [
        "# Infosys Interview Guide",
        "Test Pattern and Preparation Tips",
        "",
        "# 1. Online Test",
        "- Mathematical Ability: quants, data interpretation.",
        "- Logical Reasoning: series, puzzles, arrangements.",
        "- Verbal Ability: grammar and comprehension.",
        "- Technical/Pseudo-code section for some roles.",
        "",
        "# 2. Mathematical Ability",
        "- Percentages, averages, ratios, simple/compound interest.",
        "- Time and work, pipes, speed and distance.",
        "- Practice previous year papers to spot patterns.",
        "",
        "# 3. Logical Reasoning",
        "- Coding-decoding, number series, odd one out.",
        "- Venn diagrams, syllogisms, direction sense.",
        "",
        "# 4. Verbal Ability",
        "- Synonyms/antonyms, sentence completion, para jumbles.",
        "",
        "# 5. Technical Round",
        "- Core subjects: DBMS, OS, OOP, basic data structures.",
        "- Be ready with 2-3 strong projects from your resume.",
        "",
        "# 6. HR Round",
        "- Questions on gap years, relocation, and why Infosys.",
        "- Prepare STAR stories for teamwork and leadership.",
    ],
    "wipro_interview_guide.pdf": [
        "# Wipro Interview Guide",
        "NLTH / WILP Test Pattern and Preparation",
        "",
        "# 1. Online Assessment (NLTH)",
        "- Quantitative Aptitude: numbers, percentages, ratios.",
        "- Logical Reasoning: series, coding-decoding, puzzles.",
        "- Verbal Ability: grammar, vocabulary.",
        "- Written Communication (essay) for some roles.",
        "- Coding section for engineering roles.",
        "",
        "# 2. Quantitative Aptitude",
        "- Profit/loss, simple & compound interest, time-speed-distance.",
        "- Permutation & combination, probability basics.",
        "",
        "# 3. Logical Reasoning",
        "- Number/letter series, blood relations, seating arrangements.",
        "",
        "# 4. Verbal & Written",
        "- Error spotting, fill in the blanks, comprehension.",
        "- Write a clear, structured essay (intro, body, conclusion).",
        "",
        "# 5. Technical Interview",
        "- Fundamentals of C, Java, SQL, and web basics.",
        "- OS and networking concepts at a beginner level.",
        "",
        "# 6. HR Round",
        "- Questions about career goals and willingness to relocate.",
        "- Emphasize communication skills and adaptability.",
    ],
    "accenture_interview_guide.pdf": [
        "# Accenture Interview Guide",
        "Assessment Pattern and Preparation Tips",
        "",
        "# 1. Online Assessment",
        "- Cognitive Ability: quants, reasoning, verbal.",
        "- Pseudo-code section (programming logic).",
        "- Cloud & Networking fundamentals (newer rounds).",
        "- Coding (2 problems) for technology roles.",
        "",
        "# 2. Cognitive Ability",
        "- Percentages, averages, time & work, speed & distance.",
        "- Logical puzzles and series completion.",
        "- English grammar and reading comprehension.",
        "",
        "# 3. Pseudo-code Section",
        "- Predict output of C/Java/C++ snippets.",
        "- Understand loops, recursion, arrays, pointers basics.",
        "",
        "# 4. Cloud & Networking Basics",
        "- Know cloud models: IaaS, PaaS, SaaS, public/private/hybrid.",
        "- Basic networking: IP, DNS, HTTP/HTTPS, load balancers.",
        "",
        "# 5. Communication & HR",
        "- Accenture values innovation, inclusion, and integrity.",
        "- Be ready with examples of teamwork and leadership.",
    ],
    "cognizant_interview_guide.pdf": [
        "# Cognizant (CTS) Interview Guide",
        "Test Pattern and Preparation Tips",
        "",
        "# 1. Online Test (CTS GenC)",
        "- Quantitative Aptitude: numbers, ratios, averages.",
        "- Logical Reasoning: series, puzzles, arrangements.",
        "- Verbal Ability: grammar, vocabulary, comprehension.",
        "- Coding (for GenC Next / tech roles).",
        "",
        "# 2. Quantitative Aptitude",
        "- Percentages, profit-loss, time-work, boats-streams.",
        "- Data interpretation and basic geometry.",
        "",
        "# 3. Logical Reasoning",
        "- Coding-decoding, odd one out, direction sense.",
        "- Syllogisms and logical deduction.",
        "",
        "# 4. Verbal Ability",
        "- Error spotting, sentence improvement, fill-in-blanks.",
        "",
        "# 5. Technical & HR Rounds",
        "- Core CS fundamentals: DBMS, OS, OOP, basics of web.",
        "- Projects from resume, internships, and certifications.",
        "- HR: why Cognizant, career goals, and strengths.",
    ],
    "hr_interview_questions.pdf": [
        "# HR Interview Questions & Answers",
        "Frequently Asked Questions with Tips",
        "",
        "# 1. Tell me about yourself",
        "- Structure: Present (who you are) -> Past (achievements)",
        "- -> Future (why you fit this role). Keep it under 60 seconds.",
        "",
        "# 2. What are your strengths?",
        "- Pick 2-3 real strengths and back each with an example.",
        "- Avoid generic words like hardworking without proof.",
        "",
        "# 3. What are your weaknesses?",
        "- Choose a genuine, fixable weakness.",
        "- Immediately explain the system/action you use to improve it.",
        "",
        "# 4. Why should we hire you?",
        "- Map your skills to the job description.",
        "- Show how you add value: results, speed, teamwork.",
        "",
        "# 5. Where do you see yourself in 5 years?",
        "- Show ambition aligned with the company.",
        "- Mention growing into senior technical responsibilities.",
        "",
        "# 6. Why this company?",
        "- Research products, culture, and recent news.",
        "- Link the company mission to your career goals.",
        "",
        "# 7. Salary expectations",
        "- Give a researched range, open to discussion.",
        "- Focus on total compensation, not just base.",
        "",
        "# 8. Do you have any questions?",
        "- Ask about team, growth, tech stack, or culture.",
        "- Never ask about salary/perks first.",
    ],
    "aptitude_formulas.pdf": [
        "# Aptitude Formula Sheet",
        "Quick revision for placement tests",
        "",
        "# 1. Percentages",
        "- x% of y = y% of x.",
        "- Increase by r% then decrease by r% -> net change = -(r^2/100)%.",
        "",
        "# 2. Profit & Loss",
        "- Profit% = (Profit / CP) * 100.",
        "- SP = CP * (1 + Profit%/100) or CP * (1 - Loss%/100).",
        "- Discount% = (Discount / MP) * 100.",
        "",
        "# 3. Simple & Compound Interest",
        "- SI = (P * R * T) / 100.",
        "- CI = P * (1 + R/100)^T - P.",
        "",
        "# 4. Time & Work",
        "- Work = Rate * Time. Combined rate = sum of individual rates.",
        "- If A is twice as good as B, A takes half the time.",
        "",
        "# 5. Time, Speed & Distance",
        "- Speed = Distance / Time.",
        "- km/h to m/s: multiply by 5/18.",
        "- Downstream = (boat + stream), Upstream = (boat - stream).",
        "",
        "# 6. Averages",
        "- Average = Sum of items / Number of items.",
        "- Weighted average for groups.",
        "",
        "# 7. Ratio & Proportion",
        "- a:b = c:d implies ad = bc.",
        "- Partnership: profit shared in ratio of (capital * time).",
        "",
        "# 8. Probability & Combinations",
        "- Probability = Favorable / Total.",
        "- nCr = n! / (r! * (n-r)!), nPr = n! / (n-r)!.",
        "- For 2 dice: total outcomes = 36.",
    ],
    "resume_building_guide.pdf": [
        "# Resume Building Guide",
        "Format, Keywords, and Common Mistakes",
        "",
        "# 1. Structure",
        "- Contact info, summary, education, skills, projects,",
        "- internships, achievements, certifications.",
        "- One page for freshers, two pages max for experienced.",
        "",
        "# 2. Write Impactful Bullets",
        "- Start with action verbs: Built, Optimized, Designed, Led.",
        "- Add metrics: improved X% faster, reduced cost by Y, served Z users.",
        "- Format: Action + What + Result.",
        "",
        "# 3. ATS-Friendly Formatting",
        "- No tables, images, or fancy graphics (ATS bots misread them).",
        "- Use standard section headings.",
        "- Match keywords from the job description.",
        "",
        "# 4. Skills Section",
        "- Group into Languages, Frameworks, Tools, Soft skills.",
        "- Rate honestly - be ready to answer on anything listed.",
        "",
        "# 5. Projects",
        "- 2-3 strong projects beat 10 weak ones.",
        "- Include tech stack, your role, and measurable outcome.",
        "- Link to live demo or GitHub repo.",
        "",
        "# 6. Common Mistakes to Avoid",
        "- Typos and inconsistent formatting.",
        "- Generic objectives instead of a tailored summary.",
        "- Lying about skills or dates - it is caught in interviews.",
    ],
}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for filename, lines in PDFS.items():
        path = os.path.join(OUT_DIR, filename)
        with open(path, "wb") as f:
            f.write(build_pdf(filename, lines))
        print(f"wrote {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
