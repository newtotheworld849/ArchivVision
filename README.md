## 4. Execution & Evaluation Modes
This repository contains two execution targets to demonstrate both live API infrastructure and robust offline sandbox testing:

### Mode A: Live Production API
To run the active machine learning pipeline utilizing live Vision-LLM endpoints:
```bash
streamlit run app.py
```
*(Requires a valid `OPENAI_API_KEY` configured within your local `.env` file).*

### Mode B: Offline Sandbox Evaluation (Out-of-the-Box)
To inspect the relational database layout and user interface flows completely offline without credit constraints:
```bash
streamlit run app_offline.py
```
*(This deployment utilizes a localized mock wrapper. The included `archive.db` and `archive_vault/` folders are pre-populated with live testing records for immediate assessment).*
