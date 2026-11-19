class RecommendationService:
    """
    Validated Agricultural Guidance Engine.
    Provides agronomic, preventive, and cultural advice without prescribing
    unregulated or hazard-prone chemical dosages.
    """

    GUIDANCE_CATALOG = {
        "Tomato___healthy": {
            "title": "Healthy Crop Maintenance Protocol",
            "summary": "Foliage exhibits vigorous vegetative condition. Maintain current stewardship practices.",
            "immediate_actions": [
                "Continue standard drip irrigation schedules maintaining uniform soil moisture.",
                "Ensure adequate calcium nutrition to prevent blossom end rot in subsequent fruiting.",
                "Regularly scout the undersides of lower leaves weekly for early pathogen onset."
            ],
            "cultural_practices": [
                "Maintain 45–60 cm plant spacing to promote sunlight penetration and air circulation.",
                "Apply organic straw mulch (5 cm layer) to prevent soil splashing onto foliage.",
                "Disinfect pruning shears with 70% isopropyl alcohol between rows."
            ],
            "prevention": [
                "Rotate solanaceous crops with legumes or brassicas on a 3-year cycle.",
                "Avoid overhead sprinkler irrigation; always irrigate at the base of the plant."
            ],
            "regulatory_warning": "Routine preventative spraying is not advised on healthy foliage. Conserve beneficial insect predators."
        },
        "Tomato___Early_blight": {
            "title": "Early Blight Management Protocol (Alternaria solani)",
            "summary": "Foliar fungal pathogen characterized by concentric ring lesions ('target board' effect) on older leaves.",
            "immediate_actions": [
                "Prune and carefully remove severely spotted lower leaves using clean pruners; bag and burn or deeply bury debris (do not compost).",
                "Immediately discontinue any overhead sprinkler watering to prevent spore dispersal.",
                "Inspect adjacent plants within 5 meters for early target lesions."
            ],
            "cultural_practices": [
                "Stake and trellis vines to elevate foliage at least 30 cm above ground level.",
                "Apply organic pine bark or straw mulch under plants to create a barrier against soil-borne spores.",
                "Prune suckers on clear sunny mornings so pruning wounds dry and callus quickly."
            ],
            "prevention": [
                "Practice 3-year crop rotation away from solanaceous crops (tomatoes, potatoes, eggplants).",
                "Select resistant or tolerant tomato varieties (e.g., Mountain Supreme, Defiant) in future plantings."
            ],
            "regulatory_warning": "Consult your local Agricultural Extension Office or KVK agronomist for certified bio-fungicide options (e.g. Bacillus subtilis or registered copper hydroxide). Never apply uncertified synthetic fungicides without licensed agrochemical consultation."
        },
        "Tomato___Late_blight": {
            "title": "Late Blight Emergency Protocol (Phytophthora infestans)",
            "summary": "High-risk water-mold oomycete causing rapid water-soaked lesions, greasy dark stems, and potential total crop loss in humid conditions.",
            "immediate_actions": [
                "ALERT: Quarantine the affected row immediately. Late blight spreads rapidly on wind and water droplets.",
                "Remove and bag infected plant tissues during dry midday conditions. Do not shake foliage.",
                "Notify regional agronomic extension officers if regional outbreaks are under tracking."
            ],
            "cultural_practices": [
                "Increase greenhouse ventilation or field spacing immediately to drive relative humidity below 80%.",
                "Strictly prohibit walking through wet crops to avoid mechanical spore transmission on clothing and tools.",
                "Destroy volunteer tomato and potato plants in surrounding field borders."
            ],
            "prevention": [
                "Ensure field rows are oriented parallel to prevailing winds for maximum canopy drying.",
                "Plant certified disease-free transplants and certified seed potatoes."
            ],
            "regulatory_warning": "Late blight requires immediate expert intervention. Contact a licensed plant pathologist or extension agent immediately for emergency registered protective treatments. Do not purchase unregistered chemicals."
        },
        "Tomato___Bacterial_spot": {
            "title": "Bacterial Spot Management Protocol (Xanthomonas spp.)",
            "summary": "Bacterial pathogen forming small dark, greasy, water-soaked lesions that may cause defoliation and fruit blemishes.",
            "immediate_actions": [
                "Never touch, prune, or harvest from plants while foliage is wet with rain or dew.",
                "Sanitize all farm equipment, trellising stakes, and tools with 10% bleach or quaternary ammonium solution.",
                "Remove heavily blighted leaves from lower canopy."
            ],
            "cultural_practices": [
                "Use drip tape or micro-sprinklers positioned near ground level.",
                "Avoid excessive nitrogen fertilization, which produces lush, succulent tissue highly susceptible to bacterial penetration."
            ],
            "prevention": [
                "Treat seeds with hot water (50°C for 25 minutes) before germination to eradicate seed-borne bacterial inocula.",
                "Implement strict 2-year rotation with non-host crops like sweet corn or beans."
            ],
            "regulatory_warning": "Antibiotics are strictly restricted in agriculture in most jurisdictions. Consult local agricultural authorities for approved fixed-copper or copper + mancozeb combination guidelines where officially registered."
        },
        "Tomato___Septoria_leaf_spot": {
            "title": "Septoria Leaf Spot Protocol (Septoria lycopersici)",
            "summary": "Fungal leaf disease producing numerous circular spots with dark brown margins and sunken gray centers on lower leaves.",
            "immediate_actions": [
                "Strip bottom 25-30 cm of foliage as plants grow to eliminate the primary ladder for spore ascent.",
                "Collect fallen diseased leaf litter immediately from the soil surface.",
                "Ensure weed management around field perimeters (horse nettle and black nightshade are alternate hosts)."
            ],
            "cultural_practices": [
                "Apply clean plastic or organic mulch to prevent rain-splash inoculum.",
                "Provide sturdy tomato cages to promote upright growth."
            ],
            "prevention": [
                "Perform thorough post-harvest tillage or residue removal to bury overwintering pycnidia.",
                "Rotate away from solanaceous plants for at least 2 seasons."
            ],
            "regulatory_warning": "Organic growers may consult local extension specialists regarding potassium bicarbonate or bio-fungicide registrations."
        },
        "Tomato___Leaf_Mold": {
            "title": "Leaf Mold Management Protocol (Passalora fulva)",
            "summary": "Foliar fungus common in high-humidity greenhouses, causing pale yellow chlorotic patches above and olive-velvety spores beneath.",
            "immediate_actions": [
                "Immediately activate greenhouse exhaust fans and air circulation fans to drop relative humidity below 80%.",
                "Heat and vent the greenhouse during morning sunrise hours to prevent leaf condensation.",
                "Remove heavily sporulating lower leaves."
            ],
            "cultural_practices": [
                "Increase greenhouse night temperatures slightly to prevent dew point condensation on leaves.",
                "Space greenhouse containers at minimum 50 cm intervals."
            ],
            "prevention": [
                "Clean greenhouse glass and structural frames between crop seasons with agricultural sanitizers.",
                "Select tomato varieties possessing Cf resistance genes (Cf-2 to Cf-9)."
            ],
            "regulatory_warning": "Preventative bio-rational sprays must comply with greenhouse regulations. Verify label authorization for indoor structures."
        },
        "Tomato___Spider_mites_Two_spotted_spider_mite": {
            "title": "Two-Spotted Spider Mite Management (Tetranychus urticae)",
            "summary": "Arthropod pest infestation causing characteristic yellow stippling, bronzing, and delicate silk webbing under leaves in hot, dry conditions.",
            "immediate_actions": [
                "Spray affected undersides of leaves with a forceful jet of clean water to knock down mite colonies and destroy webbing.",
                "Release biological biocontrol agents such as predatory mites (Phytoseiulus persimilis or Neoseiulus californicus).",
                "Isolate infested plants to prevent dispersal along wind currents."
            ],
            "cultural_practices": [
                "Increase relative humidity in greenhouse bays; spider mites reproduce exponentially in hot, arid air (<40% RH).",
                "Mulch walkways to suppress dust, which discourages beneficial predatory insects."
            ],
            "prevention": [
                "Avoid broad-spectrum synthetic pyrethroids which eradicate natural predatory insects and trigger massive spider mite flare-ups.",
                "Scout edge rows bordering dusty roads weekly."
            ],
            "regulatory_warning": "Consider approved horticultural oils, insecticidal potassium soaps, or neem formulations applied during early morning or sunset to prevent leaf burn."
        },
        "Tomato___Target_Spot": {
            "title": "Target Spot Management (Corynespora cassiicola)",
            "summary": "Fungal disease causing pinpoint lesions that enlarge into target-like brown spots with yellow halos on leaves and stems.",
            "immediate_actions": [
                "Prune lower infected canopy and improve air circulation.",
                "Sterilize tools between plant contacts.",
                "Avoid overhead irrigation."
            ],
            "cultural_practices": [
                "Maintain uniform plant nutrition avoiding excessive vegetative vigor.",
                "Clear plant debris at end of season."
            ],
            "prevention": [
                "Rotate with non-solanaceous crops.",
                "Ensure adequate row spacing."
            ],
            "regulatory_warning": "Verify registered fungicidal options with your local agronomist."
        },
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
            "title": "Tomato Yellow Leaf Curl Virus (TYLCV) Protocol",
            "summary": "Geminivirus transmitted exclusively by the sweetpotato whitefly (Bemisia tabaci), causing stunted growth, cupped leaves, and severe flower drop.",
            "immediate_actions": [
                "CRITICAL: Rogue out (uproot and destroy in sealed bags) plants showing systemic yellow curl symptoms immediately. Viruses cannot be cured once inside plant vascular tissue.",
                "Install yellow sticky traps (1 trap per 15-20 sq meters) to monitor and suppress adult whitefly populations.",
                "Inspect greenhouse vents and doorways for insect netting integrity (use 50-mesh insect screens)."
            ],
            "cultural_practices": [
                "Reflective silver or aluminum plastic mulches repel incoming whiteflies by reflecting ultraviolet light.",
                "Eliminate weed hosts (particularly Malvaceae and Solanaceae weeds) around greenhouse perimeters."
            ],
            "prevention": [
                "Plant TYLCV-resistant hybrids (bearing the Ty-1 or Ty-3 resistance genes).",
                "Observe a regional host-free period of 6–8 weeks before transplanting new crops."
            ],
            "regulatory_warning": "Pesticides do not cure viral infections. Vector control must be coordinated with integrated pest management (IPM) guidelines."
        },
        "Tomato___Tomato_mosaic_virus": {
            "title": "Tomato Mosaic Virus (ToMV) Protocol",
            "summary": "Extremely stable mechanical virus causing mottled light/dark green foliage, leaf distortion, and stunted fruit development.",
            "immediate_actions": [
                "Immediately quarantine and remove symptomatic plants in sealed containers.",
                "Mandatory hygiene: Workers must wash hands with warm soap and water or 20% nonfat dry milk solution before touching healthy crops.",
                "PROHIBIT tobacco use on or near farm premises, as tobacco products can transmit mosaic strains."
            ],
            "cultural_practices": [
                "Dip pruners and gloves in skim milk solution (enzymatic viral inhibitor) between handling every single plant.",
                "Never take cuttings or propagation material from suspect seedbeds."
            ],
            "prevention": [
                "Select ToMV-resistant seeds (e.g. Tm-2^2 resistance gene).",
                "Soak seeds in 10% trisodium phosphate (TSP) prior to planting if seeds are not commercially certified."
            ],
            "regulatory_warning": "There are no chemical viricides for mosaic viruses. Sanitation and seed hygiene are the sole effective defenses."
        },
        "Unknown___needs_expert_review": {
            "title": "Atypical Foliar Condition — Expert Review Required",
            "summary": "The model detected abnormal visual signatures or low confidence that require human agronomic verification.",
            "immediate_actions": [
                "Flag this sample for local Extension Officer / Agronomist review using the 'Submit Expert Feedback' feature below.",
                "Capture high-resolution photographs under diffuse natural daylight showing both upper and lower leaf surfaces.",
                "Take a whole-plant photo to provide macro-context (wilt vs localized spot vs nutritional chlorosis)."
            ],
            "cultural_practices": [
                "Isolate the plant or row temporarily while diagnostic verification is in progress.",
                "Review recent irrigation, fertilizer (NPK / micronutrient), and weather logs for abiotic stress causes."
            ],
            "prevention": [
                "Maintain clean farm biosecurity and record keeping."
            ],
            "regulatory_warning": "Never apply prophylactic chemicals to unconfirmed conditions. Misapplication damages beneficial microbiology and risks regulatory violations."
        }
    }

    @classmethod
    def get_guidance(cls, disease_key: str) -> dict:
        default_guidance = cls.GUIDANCE_CATALOG.get("Unknown___needs_expert_review")
        return cls.GUIDANCE_CATALOG.get(disease_key, default_guidance)
