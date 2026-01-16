# System Architecture Trade-offs

This document records key design decisions, their rationale, and implications for the police operations AI system. Each decision represents a deliberate choice balancing immediate practicality against future scalability.

---

## 1. Frame Sampling vs. Real-time Video Streaming

**Decision:** Frame sampling every 2-5 seconds instead of continuous video processing

**Reasoning:**

- **Cost efficiency:** Processing every frame requires GPU instances costing ₹3,00,000+/month; sampling reduces compute needs by 90%
- **Computational feasibility:** Single-node deployment can handle 10-15 camera feeds simultaneously with sampling; streaming would require distributed processing
- **Use-case alignment:** Police incidents (crowd surges, abandoned objects, route violations) develop over 30+ seconds; 5-second intervals provide adequate early warning

**Alternatives Considered:**

- *Motion-triggered processing:* Discarded due to sensitivity calibration issues and missed events in complex scenes
- *Edge AI devices:* Cost-prohibitive at ₹15,000+ per camera for police budget constraints
- *Cloud GPU streaming:* Rejected due to data sovereignty concerns (sensitive police footage leaving premises)

**Trade-offs & Limitations:**

- **Detection latency:** Maximum 5-second delay in alert generation; may miss very fast-moving threats (e.g., drive-by incidents)
- **Temporal blind spots:** Events occurring between sampled frames go undetected (though statistically rare for target use cases)
- **Frame quality dependency:** Alerts only as good as the specific frames captured; motion blur in sampled frames reduces accuracy

**Future Improvements:**

- Adaptive sampling: Reduce interval to 1-2 seconds when preliminary detection triggers (e.g., crowd density &gt;70% threshold)
- Hybrid approach: Deploy edge processing for critical feeds (VIP route cameras) while maintaining sampling for general surveillance
- Motion-compensated sampling: Use optical flow analysis to sample more frequently when movement detected

---

## 2. Rule-based vs. ML-based Anomaly Detection

**Decision:** Rule-based heuristics instead of machine learning models

**Reasoning:**

- **Zero training data requirement:** Police departments lack labeled historical datasets of "anomalous" vs "normal" scenarios
- **Interpretability & accountability:** Officers and courts can understand "if crowd_density &gt; 7 AND duration &gt; 180s THEN alert"; black-box ML decisions face legal challenges
- **Bias mitigation:** Rules can be explicitly audited for fairness; ML models trained on biased policing data perpetuate discrimination
- **Debuggability:** When system flags false positives, rules can be tuned transparently; ML debugging is opaque

**Alternatives Considered:**

- *Few-shot learning:* Discarded due to unreliable accuracy (&gt;20% false positive rates) in initial tests
- *Pre-trained urban surveillance models:* Rejected due to domain mismatch (Western city models perform poorly on Indian street scenes)
- *Crowdsourced labeling:* Unviable due to data sensitivity (cannot expose police footage to external annotators)

**Trade-offs & Limitations:**

- **Detection sophistication:** Cannot identify complex patterns (e.g., coordinated group behavior across multiple feeds)
- **Manual rule curation:** Each new scenario requires explicit rule definition; lacks ML's adaptability
- **Edge case blindness:** Rules miss anomalies that don't match predefined patterns (unknown-unknown risks)

**Future Improvements:**

- Semi-supervised learning: Gradually introduce ML components as department accumulates labeled incident data (2-3 years)
- Rule confidence scoring: Add probabilistic weights to rules based on historical validation
- Anomaly library: Build repository of validated edge cases to expand rule sets systematically

---

## 3. Synchronous vs. Asynchronous Processing

**Decision:** Asynchronous for computer vision tasks; synchronous for API responses

**Reasoning:**

- **Non-blocking CV pipeline:** Frame processing runs in background threads; main application remains responsive during heavy computation
- **Guaranteed API reliability:** Officers receive immediate confirmation (200 OK) that alert was received; critical for trust in system
- **Resource efficiency:** Async CV allows dynamic scaling of worker threads based on queue depth; prevents thread pool exhaustion
- **Fault isolation:** CV task failures don't crash API server; ensures reporting functions remain available even if analytics fail

**Alternatives Considered:**

- *Fully synchronous:* Risked API timeouts (&gt;30s) during CV model loading or processing spikes
- *Fully asynchronous:* Complex callback chains made debugging officer-facing bugs difficult; risked losing critical alerts in message broker failures
- *Event-driven microservices:* Added unnecessary complexity for single-department deployment (no cross-agency scaling needs)

**Trade-offs & Limitations:**

- **Implementation complexity:** Developers must manage thread safety, callback hell prevention, and eventual consistency
- **Alert delay variability:** Async queue depth introduces unpredictable latency (2-10 seconds vs. constant 5s with pure sampling)
- *Debugging difficulty:* Tracing alert from camera → CV worker → API → officer requires correlation IDs across async boundaries

**Future Improvements:**

- Migrate to async/await pattern (Python 3.11+) for better code readability while maintaining performance
- Implement priority queue for CV tasks: VIP route cameras processed ahead of general surveillance
- Add sync fallback: If async queue exceeds threshold, switch to direct processing to guarantee maximum latency SLAs

---

## 4. Local Deployment vs. Cloud

**Decision:** Local single-node deployment (on-premise server)

**Reasoning:**

- **Data privacy & sovereignty:** Police footage contains sensitive information; Indian PDP Bill 2023 restricts cross-border data flows; cloud storage creates legal vulnerabilities
- **Cost predictability:** One-time server cost (₹2,00,000) vs. recurring cloud costs (₹40,000-60,000/month for comparable GPU instances)
- **Network resilience:** Functions during internet outages (critical during emergency bandobast when connectivity often fails)
- **Vendor lock-in avoidance:** No dependency on foreign cloud providers (AWS, Azure) for critical policing infrastructure

**Alternatives Considered:**

- *Government cloud (MeghRaj):* Rejected due to lengthy procurement cycles (12-18 months) and limited GPU availability
- *Hybrid cloud:* Sensitive CV processing on-premise, analytics in cloud; rejected due to complex data classification requirements beyond department capacity
- *Multi-department shared cloud:* Legal barriers prevent sharing infrastructure between state and central police forces

**Trade-offs & Limitations:**

- **Scalability ceiling:** Single server limited to ~20 camera feeds; cannot scale horizontally without architecture redesign
- **Maintenance burden:** Requires in-house IT staff for server management, backups, security patching
- **Hardware failure risk:** No automatic failover; server crash means complete system outage (estimated 24-48 hour recovery time)
- **Limited compute power:** Cannot run latest large models (e.g., YOLOv8 segmentation) at usable frame rates

**Future Improvements:**

- Containerize application (Docker/Kubernetes) for eventual migration to private cloud when department infrastructure matures
- Implement warm standby server with database replication; manual failover during planned maintenance
- Edge-device federation: Process non-critical feeds on low-cost edge devices; reserve server for high-priority bandobast cameras

---

## 5. Alert Sensitivity Thresholds

**Decision:** Conservative initial thresholds with officer-adjustable overrides

**Reasoning:**

- **Prevent alert fatigue:* Low thresholds generate 50-100 false positives/day, causing officers to ignore system; conservative settings target &lt;5 alerts/shift
  - **Build trust gradually:* High-accuracy early alerts establish credibility; sensitivity can be increased after 6 months of validated data*
  - **Officer autonomy:* Field supervisors can adjust thresholds for specific events (e.g., lower threshold during high-alert bandobast)*

 ** Specific Choices: **

- Crowd density: Alert at 7 persons/m² (research indicates 10+/m² creates stampede risk; 7 provides buffer)
- Abandoned object: Time threshold 10 minutes (allows for legitimate temporary objects; reduces false positives)
- Route violation: 3 standard deviations from normal traffic flow (accounts for normal congestion variance)

 ** Alternatives Considered: *

- *Adaptive thresholds:* Discarded; risked self-reinforcing loops (system adapts to officer ignoring alerts, becomes even less sensitive)
- *ML-optimized thresholds:* Rejected; requires labeled false positive dataset unavailable in initial deployment

**Trade-offs & Limitations:**

- **Missed early warnings:** Conservative settings may delay detection of genuinely developing incidents by 15-30 seconds
- **Manual tuning overhead:** Supervisors must adjust thresholds for each bandobast scenario; lacks "set and forget" convenience
- **One-size-fits-all:** Same thresholds applied across diverse camera scenes (market vs. residential vs. arterial road)

**Future Improvements:**

- Implement scene-specific profiles: Market area cameras use different thresholds than residential areas
- Add "learning mode": System logs officer dismissals to identify patterns in false positives and suggest threshold adjustments
- Tiered alerting: "Info" level for low confidence (sent to control room dashboard only), "Alert" for high confidence (pushed to field officers)

---

## 6. Mobile App vs. Web Dashboard

**Decision:** Progressive Web App (PWA) instead of native mobile app + separate web dashboard

**Reasoning:**

- **Development velocity:* Single codebase serves both desktop (control room) and mobile (field officers); 50% less development effort
  - **Offline capability:* Service workers cache critical data; officers view last-known camera status even in network dead zones (common in bandobast areas)
  - **No app store dependency:* Bypasses Google Play review delays; immediate updates for security patches or new features
  - *Device compatibility:* Works on department-issued Android tablets and officers' personal smartphones equally

 ** Alternatives Considered: *

- *Native Android app:* Superior performance but requires separate Kotlin development team; Play Store policy risks for police surveillance features
- *React Native:* Unnecessary complexity for single-platform (Android) deployment
- *Pure web dashboard:* No push notifications for critical alerts; officers must manually refresh

**Trade-offs & Limitations:**

- **Performance gap:** PWA responsiveness 200-300ms slower than native; may feel sluggish on low-end department devices (2GB RAM)
- **Limited hardware access:** Cannot access advanced features like Bluetooth beacons for indoor positioning or fingerprint authentication
- **Browser dependency:** Chrome/WebView bugs or updates could break functionality; less control than native app

**Future Improvements:**

- Wrap PWA in Trusted Web Activity (TWA) for Play Store distribution while maintaining web codebase
- Implement background sync: Alert acknowledgments queue during network outages and sync automatically when connectivity restored
- Add biometric authentication via WebAuthn API for officer identity verification

---

## 7. Data Retention Policy

**Decision:** 72-hour raw footage retention; 1-year structured alert metadata

**Reasoning:**

- **Privacy by design:** Automatic deletion after 72 hours prevents mass surveillance databases; aligns with "purpose limitation" principle
- **Investigation window:* * 3 days covers 99% of incident reports (most reports filed within 24-48 hours)*
- *Storage cost management:* Raw video at 15 feeds × 24hrs × 30 days = 32TB/month; 3-day retention keeps storage under 4TB
- *Historical analysis:* Metadata (alert type, location, timestamp) retained for 1 year allows crime pattern analysis without privacy-invasive long-term video storage*

 ** Specific Policy: **

- *Sampled frames:* Deleted after 72 hours regardless of alerts
- *Alert-triggered clips:* 30-second video clips around alert events retained for 90 days (investIGATION cycle)
- *Aggregated stats:* Daily summaries (camera uptime, alert counts) retained indefinitely for performance auditing

 ** Alternatives Considered: *

- *30-day retention:* Rejected due to privacy risks and storage costs (~₹50,000/month HDD expansion)
- *Metadata-only (no video):* Insufficient for alert verification; officers need visual confirmation before responding
- *indefinite storage:* Clear violation of privacy principles; legal liability under developing PDP Bill framework

**Trade-offs & Limitations:**

- **Lost evidence:** Incidents reported after 72 hours cannot be visually verified (though rare—most post-event reports within 24hrs)
- *Storage management overhead:* Automated deletion scripts require maintenance; risk of accidental mass deletion*
- *Limited training data:* Cannot retroactively label incidents for ML model training due to video deletion

**Future Improvements:**

- Implement "archive on alert" feature: Officer can flag specific incident for extended retention (max 1 year) with written justification
- Migrate to encrypted object storage (MinIO) with tamper-evident logging for chain of custody requirements
- Add video redaction API: Auto-blur faces in retained clips before sharing with external agencies (prosecutors, media)

---

## Honest System Limitations

**What the system cannot do well (by design):**

1. **Night/low-light performance:** Rule-based CV relies on visible features; performance drops &gt;40% after sunset without IR cameras
2. **Complex social anomaly detection:* Cannot recognize pre-planned criminal coordination (e.g., 5-person team dispersing for theft); only flags physical world violations (crowd, objects, routes)
3. *Long-range forecasting:* No predictive capability beyond immediate detection; cannot forecast crime trends for next week/month
4. *Adversarial robustness:* Deliberate attempts to fool system (camouflage, decoy objects) will succeed; system designed for opportunistic crime, not counter-terrorism
5. *Multi-language support:* Alert descriptions and UI currently in English/Hindi; regional language support requires additional NLP investment

**Technical debt incurred:**

- Monolithic architecture: Faster initial development but will require refactoring for multi-department deployment (estimated 6-month effort)
- Hardcoded camera configs: Each new camera requires manual JSON editing; lacks auto-discovery (future ONVIF integration needed)
- No CI/CD pipeline: Manual deployment process; acceptable for single server but error-prone for scale

---

## When to Revisit These Decisions

**Scheduled review timeline:**

- **3 months post-deployment:** Evaluate alert threshold effectiveness; adjust based on false positive rate data
- **6 months:** Assess async processing queue depth patterns; consider upgrading to dedicated GPU server if queue &gt;30s routinely
- **12 months:** Review retention policy compliance with enacted PDP Bill; adjust if legal framework changes
- **18 months:** Reconsider cloud vs. on-premise if Government e-Marketplace (GeM) cloud procurement simplifies

**Trigger conditions for immediate review:**

- False positive rate exceeds 20% for 2 consecutive weeks
- Server hardware failure requiring &gt;24hr recovery
- New law explicitly prohibiting any AI-assisted surveillance (system would pivot to pure reporting tool)
- Successful pilot in neighboring police department requiring multi-department data sharing

---

*Document Version: 1.0*
*Last Updated: January 2025*
