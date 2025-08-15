# BigQuery AI Hackathon Survey Response

## Team Experience and Feedback

### 1. BigQuery AI Experience

**Please tell us how many months of experience with BigQuery AI each team member has.**

**Team Member 1:** 2-3 months – learned and implemented during hackathon with some exposure from WGU courses.

### 2. Google Cloud Experience

**Please tell us how many months of experience with Google Cloud each team member has.**

**Team Member 1:** 2-3 months – prior projects and hackathon work

### 3. Technology Experience Feedback

**We'd love to hear from you and your experience in working with the technology during this hackathon, positive or negative. Please provide any feedback on your experience with BigQuery AI.**

Working with BigQuery AI was a highly positive experience for our team. We were able to quickly integrate `ML.GENERATE_EMBEDDING` and `ML.VECTOR_SEARCH` into a multimodal ingestion and triage pipeline that handled text, PDFs, images (OCR), and logs.

The native BigQuery ML functions allowed us to keep the architecture simple, scalable, and cost-efficient while still delivering advanced semantic search and classification capabilities. The ability to stub BigQuery calls locally helped reduce costs during development and enabled rapid iteration.

**Challenges encountered:**
- Understanding the nuances of vector search tuning (e.g., choosing k, weighting graph expansion)
- Managing quota/limits while processing larger batches of embeddings
- Regional availability issues for certain models, but worked around them by designing for idempotent creation and flexible configuration

**Overall Assessment:**
We found BigQuery AI to be a powerful, production-ready tool for retrieval-augmented AI applications. The integration with our dashboard and evaluation framework worked smoothly and opens up exciting opportunities for real-world deployment.

---

## Project Highlights

### What We Built
- **Multimodal AI Triage System**: Integrated text, PDF, image (OCR), and log processing
- **Semantic Search Pipeline**: Vector embeddings with hybrid retrieval
- **Real-time Dashboard**: Streamlit analytics with BigQuery views
- **Smart Routing**: ML-powered query classification and strategy selection
- **Production-Ready**: Environment-based configuration with security best practices

### Key BigQuery AI Features Used
- `ML.GENERATE_EMBEDDING`: Text-to-vector conversion for semantic search
- `ML.VECTOR_SEARCH`: Efficient similarity search across large datasets
- Remote Models: Vertex AI integration through BigQuery
- BigQuery ML: Logistic regression for intelligent routing

### Technical Achievements
- **Cost-Effective Development**: Local stubbing reduced development costs
- **Scalable Architecture**: BigQuery-native processing handles large datasets
- **Performance Optimization**: Graph expansion and neighbor relationships
- **Evaluation Framework**: Comprehensive metrics (NDCG@5, MRR, hit rate)
- **Security Focus**: Environment variables, secret scanning, data sanitization

### Future Opportunities
The foundation we built during this hackathon provides a solid base for:
- Enterprise knowledge management systems
- Customer support automation
- Document intelligence platforms
- Multi-tenant SaaS offerings with BigQuery AI at the core

---

*Survey completed: August 15, 2025*
*Project: projectNorthStar - AI-assisted triage & knowledge retrieval*
