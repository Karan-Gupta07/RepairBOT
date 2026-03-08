Our Reactiv Clip code to make this a Apple App Clip is in this repo: https://github.com/4ppleSA0CE/reactivapp-clipkit-lab

Reparo
Reparo is a computer vision powered repair assistant that identifies broken components from an image, generates a repair plan, and automatically finds the parts needed to complete the repair.

Overview
Reparo converts a photo of a damaged object into a structured repair workflow. The system identifies the failed component using a vision model, generates a repair guide using Gemini, and retrieves replacement parts and tools from online retailers. The goal is to connect visual damage detection directly to actionable repair instructions and purchasable components.

Architecture
The system consists of three main components:

1. Mobile Client
The client application was built using Swift with Reactiv and deployed as an App Clip. This allows users to start the repair flow without installing a full application.

Responsibilities:

Capture image of damaged object
Upload image to backend API
Display repair instructions and repair metadata
Render purchasable parts and tools
2. Backend Orchestration
The backend is implemented in Python and manages the AI pipeline.

Responsibilities:

Receive image from client
Run image preprocessing and component identification
Structure detected damage metadata
Send structured context to the Gemini API
Parse Gemini output into a standardized repair format
The repair format includes:

repair steps
estimated cost
difficulty rating
repairability score
required parts and tools
3. Product Discovery Pipeline
Once required parts are identified, the system searches for purchasable items.

Pipeline:

Query SerpAPI to locate relevant products
Identify Shopify storefronts
Retrieve product metadata using Shopify JSON endpoints
Format items into a purchasable cart structure
This allows repair instructions to directly map to real products.

Data Flow
User captures image in App Clip
Image is sent to backend API
Vision model identifies failed component
Structured damage metadata is created
Metadata is passed to Gemini for repair reasoning
Gemini returns repair steps and required items
Product discovery retrieves purchasable parts
Client renders repair guide and parts list
Challenges
Mapping AI output to real commerce
Gemini outputs repair recommendations, but these must be converted into concrete product searches. The main challenge was structuring the output so it could reliably map to purchasable items.

Product retrieval
Shopify storefronts expose consistent JSON product structures. Leveraging these endpoints allowed us to programmatically retrieve product information and build a working cart.

Mobile integration
Integrating Reactiv with Swift required additional work to ensure a seamless purchasing flow inside the App Clip environment.

Future Work
Planned improvements include:

AR repair guidance using visual overlays for part placement
expanded component detection models
improved part matching accuracy
integration with local retailers for in-store pickup
Built With
Swift
Reactiv
Python
Gemini
SerpAPI
Shopify APIs
