"""
Conversation topics data for the chatbot study platform.
Contains topic areas, specific questions, primary exiles, intensity levels, and stance data.
"""

CONVERSATION_TOPICS = [
    {
        "id": 1,
        "topic_area": "Worker Rights",
        "specific_question": "Employer monitoring of remote workers",
        "primary_exile": "Powerless",
        "intensity": "low",
        "intensity_symbol": "🟢",
        "stances": {
            "conservative": {
                "pro": "Employers have the right to ensure productivity and protect company assets; monitoring ensures accountability in a remote environment.",
                "con": "Excessive surveillance can undermine employee trust and morale, reducing long-term productivity and loyalty.",
                "neutral": "Monitoring policies should be clearly defined, proportional to the role, and communicated transparently to employees."
            }
        }
    },
    {
        "id": 2,
        "topic_area": "Worker Rights",
        "specific_question": "Living wage for all jobs",
        "primary_exile": "Shame-Filled",
        "intensity": "low",
        "intensity_symbol": "🟢",
        "stances": {
            "conservative": {
                "pro": "A baseline standard of living supports family stability and reduces dependency on government welfare programs.",
                "con": "Government-mandated living wages distort free markets, hurt small businesses, and can increase unemployment.",
                "neutral": "Market forces, regional cost-of-living differences, and business viability should all factor into wage policy discussions."
            }
        }
    },
    {
        "id": 3,
        "topic_area": "Worker Rights",
        "specific_question": "Salary transparency at work",
        "primary_exile": "Invisible",
        "intensity": "low",
        "intensity_symbol": "🟢",
        "stances": {
            "conservative": {
                "pro": "Transparency can reduce discrimination and ensure merit-based pay is verifiable, aligning with fairness values.",
                "con": "Salary disclosure can create workplace resentment, invade individual privacy, and interfere with employer-employee negotiations.",
                "neutral": "Voluntary transparency or range disclosure may balance employee awareness with business flexibility."
            }
        }
    },
    {
        "id": 4,
        "topic_area": "Social Dynamics",
        "specific_question": "Obligation to stay close to family",
        "primary_exile": "Guilty",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "Family is the foundational unit of society; geographic and relational closeness strengthens community bonds and intergenerational support.",
                "con": "Forcing obligation can damage relationships and prevent individuals from reaching their full potential in other communities.",
                "neutral": "Family obligation varies by culture and circumstance; mutual respect and communication matter more than proximity."
            }
        }
    },
    {
        "id": 5,
        "topic_area": "Social Dynamics",
        "specific_question": "Is loneliness personal or societal?",
        "primary_exile": "Invisible",
        "intensity": "low",
        "intensity_symbol": "🟢",
        "stances": {
            "conservative": {
                "pro": "Strong communities, churches, and family structures — not government programs — are the true antidotes to loneliness.",
                "con": "Framing loneliness as purely societal removes personal responsibility for building and maintaining relationships.",
                "neutral": "Loneliness is influenced by both individual choices and broader social conditions; solutions should address both dimensions."
            }
        }
    },
    {
        "id": 6,
        "topic_area": "Social Dynamics",
        "specific_question": "Cutting off a family member",
        "primary_exile": "Abandoned",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "In cases of genuine harm or abuse, protecting oneself and one's own family unit is a responsible and moral choice.",
                "con": "Estrangement should be a last resort; reconciliation, forgiveness, and family loyalty are core virtues worth preserving.",
                "neutral": "Each situation is unique; decisions about estrangement should be made carefully, ideally with counseling and exhausted alternatives."
            }
        }
    },
    {
        "id": 7,
        "topic_area": "Immigration",
        "specific_question": "Should immigrants assimilate?",
        "primary_exile": "Shame-Filled",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "Learning the language, embracing civic values, and integrating into society strengthens national cohesion and immigrant success.",
                "con": "Mandated assimilation can be culturally coercive and erase valuable heritage that enriches the host nation.",
                "neutral": "A balance between integration into shared civic life and preservation of cultural identity benefits both immigrants and society."
            }
        }
    },
    {
        "id": 8,
        "topic_area": "Immigration",
        "specific_question": "Birthplace determining opportunity",
        "primary_exile": "Powerless",
        "intensity": "low",
        "intensity_symbol": "🟢",
        "stances": {
            "conservative": {
                "pro": "National sovereignty means countries have the right to prioritize their own citizens; birthplace-based differences are a natural outcome of this.",
                "con": "The global inequality created by birthplace is a moral challenge that should inspire generosity and better legal immigration pathways.",
                "neutral": "While birthplace creates real disparities, addressing them requires balancing national interest with humanitarian responsibility."
            }
        }
    },
    {
        "id": 9,
        "topic_area": "Immigration",
        "specific_question": "Undocumented access to services",
        "primary_exile": "Invisible",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "Basic humanitarian services like emergency medical care are reasonable, but full access incentivizes illegal entry and is unfair to legal immigrants.",
                "con": "Providing broad services to undocumented individuals is fiscally unsustainable and undermines respect for immigration law.",
                "neutral": "Distinguishing between emergency humanitarian needs and broader entitlement programs may offer a pragmatic middle ground."
            }
        }
    },
    {
        "id": 10,
        "topic_area": "Lifestyle",
        "specific_question": "Obligation to be healthy",
        "primary_exile": "Shame-Filled",
        "intensity": "low",
        "intensity_symbol": "🟢",
        "stances": {
            "conservative": {
                "pro": "Personal responsibility for one's health is a core value; individuals owe it to their families and communities to take care of themselves.",
                "con": "Moralizing health choices ignores systemic barriers like food access and healthcare costs that are beyond individual control.",
                "neutral": "Encouraging healthy lifestyles is worthwhile, but public policy and cultural messaging should avoid shaming those facing health challenges."
            }
        }
    },
    {
        "id": 11,
        "topic_area": "Lifestyle",
        "specific_question": "Child-free by choice — selfish?",
        "primary_exile": "Guilty",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "Family formation and raising children are central to a flourishing society; choosing not to participate has cultural and demographic consequences.",
                "con": "Calling a personal life decision 'selfish' is an overreach; not everyone is suited for parenthood and forcing the issue helps no one.",
                "neutral": "Whether to have children is a deeply personal decision; social encouragement of family life need not translate into judgment of those who choose otherwise."
            }
        }
    },
    {
        "id": 12,
        "topic_area": "Lifestyle",
        "specific_question": "Normalizing therapy in schools",
        "primary_exile": "Invisible",
        "intensity": "low",
        "intensity_symbol": "🟢",
        "stances": {
            "conservative": {
                "pro": "Supporting students' mental health can improve academic outcomes and reduce societal costs long-term.",
                "con": "School-based therapy can overstep parental authority, push particular ideological frameworks, and medicalize normal childhood struggles.",
                "neutral": "School counseling resources should be available and stigma-free, while parents retain oversight of their children's participation."
            }
        }
    },
    {
        "id": 13,
        "topic_area": "Institutions",
        "specific_question": "Trusting healthcare",
        "primary_exile": "Powerless",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "Medical professionals generally deserve respect and trust, though patients should remain informed and advocate for themselves.",
                "con": "Government overreach into healthcare and institutional overconfidence during events like COVID-19 justifiably eroded public trust.",
                "neutral": "Trust in healthcare should be earned through transparency, accountability, and respect for patient autonomy."
            }
        }
    },
    {
        "id": 14,
        "topic_area": "Institutions",
        "specific_question": "Social services power",
        "primary_exile": "Frightened",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "Some social services are necessary to protect the vulnerable, particularly children, when families fail.",
                "con": "Social services agencies often have too much unchecked power, can disrupt intact families, and are prone to bureaucratic overreach.",
                "neutral": "Social services should operate with clear legal standards, strong oversight, and a presumption in favor of family preservation."
            }
        }
    },
    {
        "id": 15,
        "topic_area": "Institutions",
        "specific_question": "Justice system equality",
        "primary_exile": "Invisible",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "The justice system, while imperfect, is one of the most important institutions for maintaining order and protecting individual rights.",
                "con": "Disparities in outcomes across socioeconomic and racial lines represent a failure of the system that conservatives should also want to fix.",
                "neutral": "Reform efforts should focus on procedural fairness, reducing corruption, and ensuring equal application of the law without dismantling core institutions."
            }
        }
    },
    {
        "id": 16,
        "topic_area": "Fairness",
        "specific_question": "Do people get what they deserve?",
        "primary_exile": "Powerless/Guilty",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "In a free society, hard work, good character, and personal responsibility generally lead to better outcomes — merit matters.",
                "con": "Believing too strongly that outcomes are fully deserved can lead to lack of compassion for those facing structural disadvantages.",
                "neutral": "Outcomes reflect a mix of individual effort and circumstance; holding both truths simultaneously leads to more honest policy discussions."
            }
        }
    },
    {
        "id": 17,
        "topic_area": "Fairness",
        "specific_question": "Bootstrapping narrative",
        "primary_exile": "Shame-Filled",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "The bootstrapping ideal inspires perseverance, self-reliance, and the belief that individuals have agency over their circumstances.",
                "con": "Taken too literally, it can blind people to genuine systemic barriers and foster contempt for those who struggle despite effort.",
                "neutral": "Self-reliance is a valuable cultural value, but honest acknowledgment of starting-point inequality strengthens rather than weakens the narrative."
            }
        }
    },
    {
        "id": 18,
        "topic_area": "Identity",
        "specific_question": "Reinventing yourself as an adult",
        "primary_exile": "Powerless",
        "intensity": "low",
        "intensity_symbol": "🟢",
        "stances": {
            "conservative": {
                "pro": "Personal growth, redemption, and transformation are core values — people should not be permanently defined by their past.",
                "con": "Radical self-reinvention can sometimes be a way to avoid accountability or abandon meaningful commitments and community ties.",
                "neutral": "Healthy growth involves building on one's roots rather than erasing them, balancing change with continuity and responsibility."
            }
        }
    },
    {
        "id": 19,
        "topic_area": "Identity",
        "specific_question": "Defined by worst moments",
        "primary_exile": "Guilty/Shame",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "Redemption and forgiveness are foundational values; no one should be permanently defined by their worst moments if they have shown genuine change.",
                "con": "Character matters, and past actions — especially serious ones — are relevant data points in how much trust someone deserves.",
                "neutral": "Context, accountability, and evidence of change should all factor into how much weight we give to someone's worst moments."
            }
        }
    },
    {
        "id": 20,
        "topic_area": "Identity",
        "specific_question": "Changing values from upbringing",
        "primary_exile": "Abandoned",
        "intensity": "medium",
        "intensity_symbol": "🟡",
        "stances": {
            "conservative": {
                "pro": "Careful, reasoned re-examination of inherited values is healthy and part of mature faith and character development.",
                "con": "Wholesale rejection of family and traditional values is often driven by cultural pressure rather than genuine reflection.",
                "neutral": "Individuals may legitimately update some beliefs while honoring the core wisdom passed down through family and tradition."
            }
        }
    },
]


def get_topic_areas():
    """Return a list of unique topic areas."""
    topic_areas = []
    for topic in CONVERSATION_TOPICS:
        if topic["topic_area"] not in topic_areas:
            topic_areas.append(topic["topic_area"])
    return topic_areas


def get_topics_by_area(topic_area):
    """Return all topics for a given topic area."""
    return [t for t in CONVERSATION_TOPICS if t["topic_area"] == topic_area]


def get_topic_by_id(topic_id):
    """Return a specific topic by its ID."""
    for topic in CONVERSATION_TOPICS:
        if topic["id"] == topic_id:
            return topic
    return None


def get_all_stance_types():
    """Return a list of all available stance types."""
    stances = set()
    for topic in CONVERSATION_TOPICS:
        stances.update(topic["stances"].keys())
    return list(stances)
