# Data Flow Diagrams

## 1. Camera Frame Processing Flow

```
┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌─────────────┐
│  Camera  │───▶│ Frame        │───▶│ Object        │───▶│ Detection   │
│  Feed    │    │ Processor    │    │ Detector      │    │ Events      │
└──────────┘    └──────────────┘    └───────────────┘    └─────────────┘
                      │                     │                   │
                      ▼                     ▼                   ▼
               ┌──────────────┐    ┌───────────────┐    ┌─────────────┐
               │ Preprocessing│    │ Crowd         │    │ Event       │
               │ (resize,RGB) │    │ Analyzer      │    │ Database    │
               └──────────────┘    └───────────────┘    └─────────────┘
                                          │
                                          ▼
                                   ┌───────────────┐
                                   │ Surge/Density │
                                   │ Classification│
                                   └───────────────┘
```

**Steps:**

1. Camera feed sampled at intervals (1-5 sec)
2. Frame preprocessed (letterbox, BGR→RGB)
3. YOLOv8 inference → detections
4. Crowd analyzer counts persons, calculates density
5. Events generated and stored

---

## 2. Alert Generation Flow

```
┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌─────────────┐
│ Detection│───▶│ Rule         │───▶│ Confidence    │───▶│ Alert       │
│ Events   │    │ Evaluation   │    │ Scoring       │    │ Generation  │
└──────────┘    └──────────────┘    └───────────────┘    └─────────────┘
                      │                     │                   │
                      ▼                     ▼                   ▼
               ┌──────────────┐    ┌───────────────┐    ┌─────────────┐
               │ Threshold    │    │ Deduplication │    │ Notification│
               │ Check        │    │ Logic         │    │ Push        │
               └──────────────┘    └───────────────┘    └─────────────┘
```

**Decision Points:**

- Confidence > 0.6 required
- Cooldown period (60s) for deduplication
- Severity determines notification priority

---

## 3. Patrol Session Flow

```
┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌─────────────┐
│ Patrol   │───▶│ Session      │───▶│ Activity      │───▶│ Route       │
│ Start    │    │ Creation     │    │ Logging       │    │ Tracking    │
└──────────┘    └──────────────┘    └───────────────┘    └─────────────┘
                                          │                   │
                                          ▼                   ▼
                                   ┌───────────────┐    ┌─────────────┐
                                   │ Incident      │    │ Distance    │
                                   │ Recording     │    │ Calculation │
                                   └───────────────┘    └─────────────┘
                                          │
                                          ▼
┌──────────┐    ┌──────────────┐    ┌───────────────┐
│ Summary  │◀───│ LLM          │◀───│ RAG           │
│ Output   │    │ Generation   │    │ Retrieval     │
└──────────┘    └──────────────┘    └───────────────┘
```

---

## 4. RAG Query Flow

```
┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌─────────────┐
│ User     │───▶│ Query        │───▶│ Embedding     │───▶│ FAISS       │
│ Query    │    │ Processing   │    │ Generation    │    │ Search      │
└──────────┘    └──────────────┘    └───────────────┘    └─────────────┘
                                                               │
                                                               ▼
┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌─────────────┐
│ Response │◀───│ LLM          │◀───│ Prompt        │◀───│ Context     │
│          │    │ Inference    │    │ Construction  │    │ Documents   │
└──────────┘    └──────────────┘    └───────────────┘    └─────────────┘
```

**Latency Points:**

- Embedding generation: ~50ms
- FAISS search: ~5ms
- LLM inference: 1-5s (local)

---

## 5. Error Handling Paths

```
┌──────────────────────────────────────────────────────────────────┐
│                         ERROR HANDLING                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Camera Error ──────▶ Retry 3x ──────▶ Mark Inactive ──────▶ Log │
│                                                                   │
│  CV Inference Error ─▶ Skip Frame ───▶ Continue ──────────▶ Log  │
│                                                                   │
│  DB Write Error ────▶ Retry ─────────▶ Queue ─────────────▶ Log  │
│                                                                   │
│  LLM Timeout ───────▶ Fallback ──────▶ Cached Response ───▶ Log  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```
