
def is_academic_phrase(phrase):
    if not phrase:
        return False

    # if you have academic-sounding tags, you're academic
    sciency_words = [
        "chemi",  
        "scien", 
        "bio",  
        "econo", 
        "omics",
        "sociology",
        "physics", 
        "psych", 
        "math", 
        # "statistics",
        "ecolog", 
        "genetics",
        # "analysis", 
        "department",
        "dept of",
        "university",
        "formatics",
        "evolution",

        "professor",
        "doctoral", 
        "phd", 
        "postdoc", 
        "post-doc",

        # "chemphys",  #cran tag         
        # "experimentaldesign", 
        # "clinicaltrials", 
        # "research", 
        # "medicalimaging", 
        # "differentialequations", 
        # "pharmacokinetics", 
        # "environmetrics" 
    ]

    phase_lower = phrase.lower()
    for sciency_word in sciency_words:
        if sciency_word in phase_lower:
            return True
    return False


# and not proxy_papers ilike '%@Book%' 
# and not proxy_papers ilike '%@InBook%'
# and not proxy_papers ilike '%@InPhdThesis%'
# and not proxy_papers ilike '%@PhdThesis%'
# and not proxy_papers ilike '%@Article%'
# and not proxy_papers ilike '%@InProceedings%'
# and not proxy_papers ilike '%@InCollection%'
# and not proxy_papers ilike '%@Manual%'
# and not proxy_papers ilike '%@Misc%'
# and not  proxy_papers ilike '%@Unpublished%'
# and and proxy_papers ilike '%@TechReport%'
# and not proxy_papers='No proxy paper'
# and host='cran'    