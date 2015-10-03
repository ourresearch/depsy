
def is_academic_phrase(phrase):
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
        "statistics",
        "ecolog", 
        "genetics",
        "analysis", 
        "chemphys",  #cran tag         
        "experimentaldesign", 
        "clinicaltrials", 
        "research", 
        "medicalimaging", 
        "differentialequations", 
        "pharmacokinetics", 
        "environmetrics" 
    ]

    phase_lower = phrase.lower()
    for sciency_word in sciency_words:
        if sciency_word in phase_lower:
            return True
    return False