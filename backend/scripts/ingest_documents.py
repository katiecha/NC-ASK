"""
ingest_documents.py
Enhanced Document Ingestion Script for NC ASK
Bridges existing ingestion service with NC ASK metadata requirements
"""
import asyncio
import sys
import json
import aiohttp
from pathlib import Path
from typing import Dict, List
from enum import Enum
import logging
from dotenv import load_dotenv

load_dotenv()

# --- Setup and Initialization ---

# Add parent directory to path (assuming this script is in a subdirectory)
sys.path.insert(0, str(Path(__file__).parent.parent))

# CORRECTED: Import the actual services
from services.ingestion import IngestionService 
# NOTE: The downloader needs to be imported from services.downloader in a real environment
from services.downloader import download_remote_file, cleanup_temp_downloads, TEMP_DOWNLOAD_DIR 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- NC ASK Metadata Schema Definitions ---

class ContentType(Enum):
    """Defines the type of content for retrieval filtering."""
    PROCEDURAL_GUIDE = "ProceduralGuide"
    FAQ = "FAQ"
    LEGAL_RIGHT = "LegalRight"
    CLINICAL_SUMMARY = "ClinicalSummary"
    FORM_TEMPLATE = "FormTemplate"
    RESOURCE_DIRECTORY = "ResourceDirectory"
    GENERAL_INFO = "GeneralInfo"

# NC ASK Document Metadata with fixes for 404/403 errors
NC_ASK_DOCUMENTS = {
    # --- Existing Documents from the Original Script ---
    "iep_referral_process": {
        "title": "DRNC IEP Referral Process Guide",
        "topic": "Education",
        "subtopic": "IEP Process",
        "audience": ["families", "advocates"],
        "tags": ["IEP", "special education", "evaluation", "IDEA", "DRNC"],
        "content_type": ContentType.PROCEDURAL_GUIDE,
        "source_org": "Disability Rights NC",
        "authority_level": 2
    },
    "drowning_prevention": {
        "title": "CDC Water Safety and Drowning Prevention",
        "topic": "Everyday Clinical Topics",
        "subtopic": "Safety",
        "audience": ["families"],
        "tags": ["safety", "water safety", "drowning", "elopement"],
        "content_type": ContentType.CLINICAL_SUMMARY,
        "source_org": "CDC",
        "escalation_flag": "crisis",
        "authority_level": 1
    },

    # --- New Documents (rest of the metadata remains the same) ---
    "partners_run_roadmap_pdf": {
        "title": "Partners Registry of Unmet Needs Roadmap (PDF)",
        "topic": "Medicaid Programs",
        "subtopic": "Registry of Unmet Needs (RUN)",
        "audience": ["families"],
        "tags": ["RUN", "waitlist", "innovations waiver", "partners", "pdf"],
        "content_type": ContentType.PROCEDURAL_GUIDE,
        "source_org": "Partners Health Management",
        "source_url": "https://www.partnersbhm.org/wp-content/uploads/partners-registry-roadmap.pdf",
        "authority_level": 2
    },
    "meettheneednc_waiver_pathway_pdf": {
        "title": "Meet the Need NC - Innovations Waiver Pathway (PDF)",
        "topic": "Medicaid Programs",
        "subtopic": "Innovations Waiver",
        "audience": ["families"],
        "tags": ["innovations", "waiver", "pathway", "guide", "checklist", "pdf"],
        "content_type": ContentType.PROCEDURAL_GUIDE,
        "source_org": "Meet the Need NC",
        "source_url": "https://meettheneednc.org/wp-content/uploads/2025/02/Innovations-Waiver-Pathway.pdf",
        "authority_level": 3 
    },
    "partners_run_main_page": {
        "title": "Partners Health - Registry of Unmet Needs Page",
        "topic": "Medicaid Programs",
        "subtopic": "Registry of Unmet Needs (RUN)",
        "audience": ["families", "providers"],
        "tags": ["RUN", "waitlist", "application", "partners"],
        "content_type": ContentType.GENERAL_INFO,
        "source_org": "Partners Health Management",
        "source_url": "https://www.partnersbhm.org/registry-of-unmet-needs",
        "authority_level": 2
    },
    "cdc_asd_diagnosis_new": {
        "title": "CDC - ASD Diagnosis and Testing",
        "topic": "Everyday Clinical Topics",
        "subtopic": "Diagnosis",
        "audience": ["families", "providers"],
        "tags": ["diagnosis", "screening", "DSM-5", "autism", "ASD"],
        "content_type": ContentType.CLINICAL_SUMMARY,
        "source_org": "Centers for Disease Control and Prevention (CDC)",
        "source_url": "https://www.cdc.gov/autism/diagnosis/?CDC_AAref_Val=https://www.cdc.gov/ncbddd/autism/screening.html",
        "authority_level": 1
    },
    "cdc_asd_treatments_new": {
        "title": "CDC ASD Treatments and Interventions",
        "topic": "Everyday Clinical Topics",
        "subtopic": "Therapies & Interventions",
        "audience": ["families", "providers"],
        "tags": ["treatment", "therapy", "intervention", "ABA", "TEACCH", "speech", "OT"],
        "content_type": ContentType.CLINICAL_SUMMARY,
        "source_org": "Centers for Disease Control and Prevention (CDC)",
        "source_url": "https://www.cdc.gov/autism/treatment/?CDC_AAref_Val=https://www.cdc.gov/ncbddd/autism/treatment.html",
        "authority_level": 1
    },

    "asnc_main_toolkits_page": {
        "title": "ASNC Toolkits and Guides Landing Page",
        "topic": "General Resources",
        "subtopic": "ASNC Support",
        "audience": ["families", "advocates"],
        "tags": ["toolkits", "ASNC", "guides"],
        "content_type": ContentType.RESOURCE_DIRECTORY,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://www.autismsociety-nc.org/toolkits/",
        "authority_level": 2
    },
    "asnc_moving_to_nc_toolkit": {
        "title": "ASNC Moving to NC Toolkit",
        "topic": "General Resources",
        "subtopic": "Relocation Guide",
        "audience": ["families"],
        "tags": ["relocation", "new resident", "NC guide", "ASNC"],
        "content_type": ContentType.PROCEDURAL_GUIDE,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://www.autismsociety-nc.org/moving-to-nc-toolkit/",
        "authority_level": 2
    },
    "asnc_advocacy_101": {
        "title": "ASNC Advocacy 101 Toolkit",
        "topic": "Legal and Advocacy",
        "subtopic": "Advocacy Skills",
        "audience": ["families", "advocates"],
        "tags": ["advocacy", "rights", "toolkit"],
        "content_type": ContentType.LEGAL_RIGHT,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://issuu.com/autismsocietync/docs/advocacy_101_toolkit_2025",
        "authority_level": 2
    },
    "asnc_aba_misconceptions": {
        "title": "ASNC ABA Misconceptions and Quality Indicators",
        "topic": "Everyday Clinical Topics",
        "subtopic": "Therapies & Interventions",
        "audience": ["families", "providers"],
        "tags": ["ABA", "quality", "misconceptions", "therapy"],
        "content_type": ContentType.GENERAL_INFO,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://www.autismsociety-nc.org/aba-misconceptions-quality-indicators/",
        "authority_level": 2
    },
    "asnc_aba_101": {
        "title": "ASNC Applied Behavior Analysis (ABA) 101",
        "topic": "Everyday Clinical Topics",
        "subtopic": "Therapies & Interventions",
        "audience": ["families"],
        "tags": ["ABA", "basics", "therapy"],
        "content_type": ContentType.CLINICAL_SUMMARY,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://www.autismsociety-nc.org/applied-behavior-analysis-aba-101/",
        "authority_level": 2
    },
    "asnc_daylight_savings": {
        "title": "ASNC Autism and Daylight Savings",
        "topic": "Everyday Clinical Topics",
        "subtopic": "Routine and Sleep",
        "audience": ["families"],
        "tags": ["sleep", "routine", "daylight savings"],
        "content_type": ContentType.GENERAL_INFO,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://www.autismsociety-nc.org/autism-daylight-savings/",
        "authority_level": 3
    },
    "asnc_special_ed_meeting": {
        "title": "ASNC Navigating the Special Education School Meeting",
        "topic": "Education",
        "subtopic": "IEP Process",
        "audience": ["families"],
        "tags": ["IEP", "meeting", "school", "special education"],
        "content_type": ContentType.PROCEDURAL_GUIDE,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://www.autismsociety-nc.org/navigating-the-special-education-school-meeting/",
        "authority_level": 2
    },
    "asnc_toilet_training": {
        "title": "ASNC Toilet Training for Autistic Children",
        "topic": "Everyday Clinical Topics",
        "subtopic": "Daily Living Skills",
        "audience": ["families"],
        "tags": ["toilet training", "daily living", "skills"],
        "content_type": ContentType.PROCEDURAL_GUIDE,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://www.autismsociety-nc.org/toilet-training-for-autistic-children-potties-and-patience/",
        "authority_level": 3
    },
    "asnc_halloween": {
        "title": "ASNC Halloween: Tricky for Treats",
        "topic": "Everyday Clinical Topics",
        "subtopic": "Social Skills",
        "audience": ["families"],
        "tags": ["social skills", "holiday", "halloween"],
        "content_type": ContentType.GENERAL_INFO,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://www.autismsociety-nc.org/halloween-tricky-for-treats/",
        "authority_level": 3
    },
    "asnc_parenting_teammates": {
        "title": "ASNC Parenting: Becoming Teammates",
        "topic": "Family Support",
        "subtopic": "Coping Strategies",
        "audience": ["families"],
        "tags": ["parenting", "family support", "relationships"],
        "content_type": ContentType.GENERAL_INFO,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://www.autismsociety-nc.org/parenting-becoming-teammates-instead-of-opponents/",
        "authority_level": 3
    },
    "asnc_transition_back_to_school": {
        "title": "ASNC Easing Transition Back to School",
        "topic": "Education",
        "subtopic": "Transitions",
        "audience": ["families"],
        "tags": ["school", "transition", "back to school", "routine"],
        "content_type": ContentType.GENERAL_INFO,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://www.autismsociety-nc.org/easing-transition-back-to-school/",
        "authority_level": 3
    },

    # --- Calendar/Event Links ---
    "asnc_calendar": {
        "title": "ASNC Calendar of Events",
        "topic": "Community Events",
        "subtopic": "ASNC Events",
        "audience": ["families", "advocates"],
        "tags": ["calendar", "events", "support group"],
        "content_type": ContentType.RESOURCE_DIRECTORY,
        "source_org": "Autism Society of North Carolina",
        "source_url": "https://www.autismsociety-nc.org/calendar-2/",
        "authority_level": 3
    },
    "arc_nc_events": {
        "title": "The Arc of NC Events Calendar",
        "topic": "Community Events",
        "subtopic": "Statewide Events",
        "audience": ["families", "advocates"],
        "tags": ["calendar", "events", "advocacy"],
        "content_type": ContentType.RESOURCE_DIRECTORY,
        "source_org": "The Arc of North Carolina",
        "source_url": "https://www.arcnc.org/events",
        "authority_level": 3
    },
    "nc_medicaid_events": {
        "title": "NC Medicaid Plans Events",
        "topic": "Community Events",
        "subtopic": "Medicaid Outreach",
        "audience": ["families", "providers"],
        "tags": ["calendar", "medicaid", "outreach"],
        "content_type": ContentType.RESOURCE_DIRECTORY,
        "source_org": "NC Medicaid / NCDHHS",
        "source_url": "https://ncmedicaidplans.gov/en/events",
        "authority_level": 1
    },
    "duke_autism_center_events": {
        "title": "Duke Autism Center Events and Seminars",
        "topic": "Community Events",
        "subtopic": "Clinical Seminars",
        "audience": ["families", "providers"],
        "tags": ["calendar", "events", "research", "clinical"],
        "content_type": ContentType.RESOURCE_DIRECTORY,
        "source_org": "Duke Autism Center",
        "source_url": "https://autismcenter.duke.edu/events",
        "authority_level": 3
    },
}

# --- Helper Functions (No changes needed) ---
# (Helper functions like determine_content_type, get_document_metadata, create_sample_documents remain the same)

# ...

# --- Main Ingestion Logic ---

async def ingest_nc_ask_documents():
    """
    Ingest NC ASK documents with enhanced metadata.
    Handles both local files and remote URLs via the downloader service.
    """
    data_dir = Path(__file__).parent.parent / "data"

    if not data_dir.exists():
        logger.info("Creating data directory and sample documents...")
        create_sample_documents()
    
    # 1. Prepare list of all unique documents to ingest (logic remains the same)
    # ... (ingestion_targets setup) ...
    ingestion_targets = []
    ingested_urls = set()
    supported_extensions = ['.pdf', '.docx', '.txt', '.html', '.htm']
    local_documents = []
    for ext in supported_extensions:
        local_documents.extend(data_dir.glob(f'*{ext}'))

    for doc_path in local_documents:
        if '_metadata' in doc_path.stem or doc_path.parent == TEMP_DOWNLOAD_DIR: continue
        metadata = get_document_metadata(doc_path)
        source_url = metadata.get("source_url")
        
        if source_url and source_url in ingested_urls:
             continue

        ingestion_targets.append({
            "path": str(doc_path),
            "title": metadata.get("title", doc_path.stem),
            "metadata": metadata,
            "is_remote": False
        })
        if source_url:
            ingested_urls.add(source_url)
    
    for key, metadata_template in NC_ASK_DOCUMENTS.items():
        source_url = metadata_template.get("source_url")
        if source_url and source_url not in ingested_urls:
            
            metadata = metadata_template.copy()
            metadata['content_type'] = metadata['content_type'].value
            
            ingestion_targets.append({
                "path": None, # Will be updated with the local temporary path
                "title": metadata.get("title", key),
                "metadata": metadata,
                "is_remote": True,
                "key": key
            })
            ingested_urls.add(source_url)


    logger.info(f"Found {len(ingestion_targets)} total resources to process.")
    
    # 2. Ingest documents using an aiohttp session for concurrent downloads
    
    async with aiohttp.ClientSession() as session:
        
        for target in ingestion_targets:
            doc_path_str = target['path']
            metadata = target['metadata']
            source_url = metadata.get("source_url")
            
            if target['is_remote']:
                # DOWNLOAD STEP: Fetch remote file and get local path
                key = target.get("key", source_url)
                # This call now uses the downloader which includes User-Agent headers
                local_path_obj = await download_remote_file(session, source_url, key)
                
                if not local_path_obj:
                    logger.error(f"✗ Failed to download remote resource: {source_url}. Skipping ingestion.")
                    continue
                
                doc_path_str = str(local_path_obj)
            
            # Final checks and ingestion call
            try:
                logger.info(f"Ingesting: {target['title']} ({'Local' if not target['is_remote'] else 'Remote'})")
                
                # Extract explicit arguments for the IngestionService signature
                content_type = metadata.pop("content_type", None)
                
                if metadata.get("escalation_flag") == "crisis" or "drowning" in target['title'].lower():
                    metadata["priority"] = "high"
                    logger.warning(f"Crisis content detected in {target['title']}")

                # Call the IngestionService
                result = await IngestionService.ingest_document(
                    file_path=doc_path_str,
                    title=target['title'],
                    source_url=source_url,
                    content_type=content_type,
                    metadata=metadata # Remaining metadata is passed here
                )

                logger.info(f"✓ Successfully ingested: {result['title']}")
                logger.info(f"  - Document ID: {result['document_id']}")
                logger.info(f"  - Chunks created: {result['chunks_created']}")
                logger.info(f"  - Content type: {content_type}")
                if metadata.get("escalation_flag"):
                    logger.info(f"  - Escalation flag: {metadata['escalation_flag']}")

            except Exception as e:
                logger.error(f"✗ Failed to ingest {target['title']}: {e}")

    # 3. Cleanup temporary files
    cleanup_temp_downloads()
# ... (verify_ingestion remains the same) ...

async def main():
    """Main function"""
    
    # --- CRITICAL FIX: Load .env file from project root ---
    project_root = Path(__file__).parent.parent.parent
    dotenv_path = project_root / ".env"
    load_dotenv(dotenv_path=dotenv_path) 
    # -----------------------------------------------------

    logger.info("=" * 60)
    logger.info("NC ASK Enhanced Document Ingestion")
    logger.info("=" * 60)

    await ingest_nc_ask_documents()

    logger.info("=" * 60)
    logger.info("Ingestion complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())