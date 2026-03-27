"""
Management command to load IFS Parts taxonomy data into the database.
Run with: python manage.py load_ifs_taxonomy
"""

import json
from django.core.management.base import BaseCommand
from accounts.models import IFSPart, IFSMeta


class Command(BaseCommand):
    help = 'Loads the IFS Parts taxonomy data into the database'

    def handle(self, *args, **options):
        self.stdout.write('Loading IFS Parts taxonomy data...')

        taxonomy_data = {
  "ifs_parts_taxonomy": {
    "meta": {
      "description": "A comprehensive taxonomy of IFS parts referenced in Self-Therapy (Earley), Internal Family Systems Therapy (Schwartz & Sweezy), Self-Therapy Vol. 3 (Earley), and Resolving Inner Conflict (Earley).",
      "note_on_self": "The Self is NOT a part. It is the seat of consciousness and true essence of the person, characterized by the 8 C's: Curiosity, Calm, Confidence, Connectedness, Clarity, Creativity, Courage, and Compassion. It cannot be damaged and is always present beneath the parts."
    },
    "protectors": {
      "description": "Protectors are parts that try to keep you from feeling pain. They act with positive intent, trying to help the person survive and function, but often in extreme or dysfunctional ways. There are two subtypes: Managers (proactive) and Firefighters (reactive).",
      "managers": {
        "description": "Managers proactively arrange a person's life and inner world to prevent exile pain from ever arising to consciousness. They tend to be controlling, strategic, and forward-thinking. They often carry burdens of responsibility and believe that without their vigilance, disaster would ensue. Managers are typically the parts we encounter first in IFS work, as they are most accessible to everyday consciousness.",
        "inner_critics": {
          "description": "Inner Critic parts are a major subcategory of managers. They judge, shame, push, or control the person in an attempt to make them acceptable, safe, or good enough. Despite their harmful impact on self-esteem, all Inner Critics have a positive protective intent. They are often modeled after critical parents or authority figures and are frequently polarized with a defending or rebelling part.",
          "parts": [
            {
              "id": "perfectionist",
              "name": "Perfectionist",
              "category": "protector",
              "subcategory": "manager_inner_critic",
              "description": "The Perfectionist tries to get the person to do everything to an impossibly high standard. It has very elevated standards for behavior, performance, production, and appearance, and when these aren't met, it attacks with messages that the work or person isn't good enough. It is often driven by a fear that if anything is less than perfect, the person will be judged, humiliated, or rejected — a fear rooted in childhood experiences of being criticized for mistakes.",
              "positive_intent": "To protect from judgment, shame, and rejection by ensuring the person is beyond reproach.",
              "common_behaviors": ["Prevents finishing projects", "Causes writer's block or creative paralysis", "Makes the person work far longer than necessary", "Attacks the person for any perceived flaw or error"],
              "often_polarized_with": ["Procrastinator", "Rebel"],
              "exile_protected": "A child who was judged, shamed, or ridiculed for imperfection",
              "healthy_version": "Quality capacity; Ease capacity",
              "sources": ["Earley Self-Therapy Vol.3", "Earley Self-Therapy"]
            },
            {
              "id": "taskmaster",
              "name": "Taskmaster",
              "category": "protector",
              "subcategory": "manager_inner_critic",
              "description": "The Taskmaster tries to get the person to work hard and be successful, using criticism, judgment, and shame as its primary tools. It may call the person lazy, stupid, or incompetent in order to motivate them. It operates from the belief that constant pressure is necessary to prevent failure and the humiliation that would follow. The Taskmaster often doesn't realize that its harsh approach undermines confidence and motivation rather than building them.",
              "positive_intent": "To ensure success and prevent the shame of failure or being seen as inadequate.",
              "common_behaviors": ["Constant internal pushing and nagging", "Criticizing when work stops or slows", "Creating anxiety around productivity", "Making rest feel like failure"],
              "often_polarized_with": ["Procrastinator", "Rebel"],
              "exile_protected": "A child who was judged or shamed for not being productive or successful enough",
              "healthy_version": "Work Confidence capacity",
              "sources": ["Earley Self-Therapy Vol.3", "Earley Self-Therapy"]
            },
            {
              "id": "inner_controller",
              "name": "Inner Controller / Food Controller",
              "category": "protector",
              "subcategory": "manager_inner_critic",
              "description": "The Inner Controller tries to control impulsive, addictive, or indulgent behavior such as overeating, rage, drug use, or other potentially destructive activities. When called the Food Controller, it specifically monitors eating and weight. It shames the person after bingeing or losing control, believing that shame will prevent the behavior from recurring. The irony is that its harsh tactics typically backfire, making the underlying exile feel worse and the impulsive part more desperate to act out.",
              "positive_intent": "To protect the person from physical harm, social embarrassment, loss of health, or loss of control.",
              "common_behaviors": ["Rigid rules about food, substances, or behavior", "Intense shame and self-attack after indulgence", "Constant monitoring and evaluating", "Trying to override the body's impulses through willpower"],
              "often_polarized_with": ["Indulger", "Rebel"],
              "exile_protected": "A child who was shamed for their appetites, needs, or lack of control; or one who fears the consequences of being visibly 'out of control'",
              "healthy_version": "Conscious Consumption capacity",
              "sources": ["Earley Self-Therapy Vol.3"]
            },
            {
              "id": "underminer",
              "name": "Underminer",
              "category": "protector",
              "subcategory": "manager_inner_critic",
              "description": "The Underminer works to erode the person's self-confidence and self-esteem, often telling them they are worthless, inadequate, or will never amount to anything. Its goal is to prevent the person from taking risks that might end in failure, rejection, or attack. By making the person small, it believes it can keep them safe from the danger of being exposed, criticized, or destroyed by others. It may also try to prevent the person from becoming too visible or powerful, as visibility was dangerous in their childhood environment.",
              "positive_intent": "To protect from the devastation of failure, rejection, or attack by keeping the person from taking risks.",
              "common_behaviors": ["Persistent internal messages of inadequacy", "Sabotaging confidence before important events", "Minimizing achievements", "Creating hopelessness about the future"],
              "often_polarized_with": ["Striving Part", "Inner Defender"],
              "exile_protected": "A child who was humiliated or attacked when they tried to be visible, powerful, or successful",
              "healthy_version": "Self-Esteem capacity; Courage capacity",
              "sources": ["Earley Self-Therapy Vol.3", "Schwartz IFS Therapy"]
            },
            {
              "id": "destroyer",
              "name": "Destroyer",
              "category": "protector",
              "subcategory": "manager_inner_critic",
              "description": "The Destroyer is perhaps the most extreme type of Inner Critic. It makes pervasive, global attacks on the person's fundamental worth and right to exist. It may tell the person they are evil, deeply flawed, or that the world would be better without them. It often appears as a dark, crushing force that stamps out any vitality, creativity, or desire. The Destroyer frequently operates by turning the person's own anger back against themselves, using rage to attack the self rather than anyone external.",
              "positive_intent": "Paradoxically, it may be trying to destroy the person before someone else does, believing this is a form of protection. It may also be crushing assertiveness or aliveness that was punished in childhood to prevent further harm.",
              "common_behaviors": ["Pervasive sense of worthlessness", "Feeling like one shouldn't exist", "Deadening of vitality and aliveness", "Turning anger inward as self-attack", "Contributing heavily to depression"],
              "often_polarized_with": ["Inner Defender", "Aliveness capacity"],
              "exile_protected": "A deeply shamed or terrorized child who was told or shown they had no value or right to exist",
              "healthy_version": "Peace capacity; Aliveness capacity",
              "sources": ["Earley Self-Therapy Vol.3", "Schwartz IFS Therapy"]
            },
            {
              "id": "guilt_tripper",
              "name": "Guilt Tripper",
              "category": "protector",
              "subcategory": "manager_inner_critic",
              "description": "The Guilt Tripper attacks the person relentlessly for something they did (or failed to do) that harmed someone they care about, or for violating a deeply held moral value. Unlike other Critics, it focuses on a specific action or pattern of behavior rather than attacking the person's general worth. It refuses to let the matter go, replaying the harm done and refusing forgiveness. The Guilt Tripper often becomes extreme when it is trying to prevent the person from ever doing the harmful thing again.",
              "positive_intent": "To ensure the person takes responsibility for harm done and prevents themselves from causing similar harm in the future. It cares deeply about conscience and moral integrity.",
              "common_behaviors": ["Constant replaying of a past harmful action", "Refusing to forgive oneself", "Excessive apology-seeking or reparative behavior", "Feeling permanently bad or damaged as a person"],
              "often_polarized_with": ["Self-Forgiveness capacity"],
              "exile_protected": "A child who was made to feel permanently bad for mistakes or who witnessed significant harm",
              "healthy_version": "Remorse capacity; Self-Forgiveness capacity",
              "sources": ["Earley Self-Therapy Vol.3"]
            },
            {
              "id": "conformist",
              "name": "Conformist / Molder",
              "category": "protector",
              "subcategory": "manager_inner_critic",
              "description": "The Conformist tries to get the person to fit a certain societal, cultural, or family mold. This mold can take many forms: being caring, aggressive, intellectual, polite, successful, or adhering to gender norms. It attacks the person when they deviate from this expected way of being and praises them when they conform. The Conformist often took on the values of whoever held power in the family or culture, believing that conformity was the price of acceptance and safety.",
              "positive_intent": "To ensure the person is accepted, included, and safe within their family or social group by fitting the expected mold.",
              "common_behaviors": ["Attacking individuality or difference", "Strong should/shouldn't messages about identity", "Making the person feel ashamed of aspects that don't fit the mold", "Rewarding conformity with temporary relief"],
              "often_polarized_with": ["Rebel Part", "Individuality capacity"],
              "exile_protected": "A child who was rejected, shamed, or excluded for being different or for not meeting family/cultural expectations",
              "healthy_version": "Cultural Integration capacity; Individuality capacity",
              "sources": ["Earley Self-Therapy Vol.3"]
            },
            {
              "id": "slave_driver",
              "name": "Slave Driver",
              "category": "protector",
              "subcategory": "manager_inner_critic",
              "description": "The Slave Driver is a specific named variant of the Taskmaster that appears in Earley's case examples. It relentlessly drives the person to work and produce, never allowing rest or satisfaction. Like the Taskmaster, it uses criticism and shame to motivate, but may be even more relentless in its demands. In the case example provided, it was discovered to be a young, frightened part modeling the behavior of the client's critical father, desperately trying to prevent the client from being seen as a failure.",
              "positive_intent": "To prevent the shame and judgment of failure by ensuring constant productivity and achievement.",
              "common_behaviors": ["Constant internal driving and pushing", "Making rest feel dangerous or selfish", "Creating anxiety when not working", "Never feeling satisfied with output"],
              "often_polarized_with": ["Procrastinator", "Ease capacity"],
              "exile_protected": "A child who felt judged or inadequate in the eyes of a critical parent or authority figure",
              "healthy_version": "Work Confidence capacity; Ease capacity",
              "sources": ["Earley Self-Therapy Vol.3 (George example)"]
            },
            {
              "id": "attacker",
              "name": "Attacker",
              "category": "protector",
              "subcategory": "manager_inner_critic",
              "description": "The Attacker is an extreme Inner Critic variant named in Sarah's case example. It appeared as a huge, muscular monster that physically attacked her internally. When explored through IFS, it was discovered to actually be a frightened child part that had learned to attack Sarah before her real parents could do it worse — a form of preemptive self-assault. This is a profound example of how the most intimidating Critics are often young, frightened parts doing the only thing they know to protect a wounded exile.",
              "positive_intent": "To attack the client before others can do it worse; to give the illusion of control over shame and humiliation.",
              "common_behaviors": ["Severe, relentless self-attack", "Appearing as a threatening, violent internal figure", "Making the person feel worthless and deserving of harm", "Attacking before any perceived external criticism"],
              "often_polarized_with": ["Blamer", "Inner Defender"],
              "exile_protected": "The Scared Kid — a child part carrying fear and pain from parental criticism and attack",
              "healthy_version": "Inner Mentor; Inner Champion",
              "sources": ["Earley Self-Therapy Vol.3 (Sarah example)"]
            }
          ]
        },
        "other_managers": {
          "parts": [
            {
              "id": "caretaker",
              "name": "Caretaker / Caretaking Part",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Caretaker part focuses obsessively on other people's needs, comfort, and happiness, often at the expense of the person's own needs. It may have learned in childhood that the only way to receive love was to give and give — to reverse roles with a needy or depressed parent. By taking care of others, this part protects against the exile's fear of abandonment or emptiness, believing that love must be earned through service. The Caretaker can cause the person to neglect their own needs entirely and to attract relationships where they give far more than they receive.",
              "positive_intent": "To earn love and connection by making others happy; to prevent abandonment or rejection by being indispensable.",
              "common_behaviors": ["Putting others' needs before one's own", "Feeling guilty when not caring for others", "Difficulty receiving care", "Attracting needy or demanding relationships"],
              "often_polarized_with": ["Self-Absorbed Part", "Resentful Part"],
              "exile_protected": "A child who felt empty, unloved, or abandoned, and learned that caring for others was the only way to get love",
              "healthy_version": "Caring capacity; Self-Care capacity",
              "sources": ["Earley Self-Therapy (Darlene example)", "Schwartz IFS Therapy"]
            },
            {
              "id": "people_pleaser",
              "name": "People-Pleasing Part",
              "category": "protector",
              "subcategory": "manager",
              "description": "The People-Pleasing Part tries to make others happy and agree with their views, often without even considering the person's own needs, desires, or opinions. It may try to merge with others, automatically agreeing with their beliefs and preferences. This part is driven by deep fear — of rejection, abandonment, anger, or loss of love — and believes that compliance is the only safe way to be in relationship. The People-Pleasing Part is often the precursor to Passive-Aggressive behavior, as the anger that comes from constant self-abnegation eventually seeks an outlet.",
              "positive_intent": "To maintain connection and prevent rejection, abandonment, or anger from others by being agreeable and accommodating.",
              "common_behaviors": ["Automatic agreement without considering own views", "Difficulty saying no", "Shaping behavior to fit others' expectations", "Feeling anxious when someone seems displeased"],
              "often_polarized_with": ["Passive-Aggressive Part", "Rebel Part"],
              "exile_protected": "A child who was rejected, abandoned, or hurt when they asserted themselves or disappointed others",
              "healthy_version": "Cooperation capacity; Assertiveness capacity",
              "sources": ["Earley Self-Therapy Vol.3"]
            },
            {
              "id": "pessimistic_depressing_protector",
              "name": "Pessimistic Part / Depressing Protector",
              "category": "protector",
              "subcategory": "manager",
              "description": "This part deliberately induces feelings of hopelessness and low energy in the person, not because it feels hopeless itself, but because it believes that hope leads to devastating disappointment. It may have developed after the person experienced profound losses or crushed hopes in childhood. By keeping the person's expectations low, it attempts to prevent them from being devastated when things don't work out. It is also sometimes used to suppress vitality and energy to keep exile pain from surfacing.",
              "positive_intent": "To prevent the person from feeling devastated by disappointment or overwhelmed by exile pain by keeping hope and energy low.",
              "common_behaviors": ["Persistent sense of futility", "Blocking excitement or anticipation", "Telling the person things won't work out before they try", "Making the person feel tired or flat"],
              "often_polarized_with": ["Aliveness capacity", "Striving Part"],
              "exile_protected": "A child whose hopes were repeatedly and painfully dashed; or exiles carrying intense emotional pain",
              "healthy_version": "Aliveness capacity; Hope",
              "sources": ["Earley Self-Therapy Vol.3", "Schwartz IFS Therapy"]
            },
            {
              "id": "depressor",
              "name": "Depressor",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Depressor is a specific type of Depressing Protector that appears in Bree's case example. It was slumped and tried not to move, because any activity caused intense body pain. It was protecting a deeply wounded exile and had learned that keeping the person inactive and depressed was the safest way to prevent that exile's pain from flooding through. The Depressor illustrates how depression can function as a protective strategy — not as a direct expression of exile pain, but as a deliberate dampening of all experience to prevent something worse.",
              "positive_intent": "To protect from being overwhelmed by the intense pain of the protected exile by keeping the person's activity and affect flat.",
              "common_behaviors": ["Heavy depression and lack of motivation", "Lethargy and physical heaviness", "Inability to move forward in life", "Preventing the person from trying things that might trigger exile pain"],
              "often_polarized_with": ["Aliveness capacity"],
              "exile_protected": "A deeply shamed or physically abused child carrying intense pain",
              "healthy_version": "Aliveness capacity",
              "sources": ["Earley Self-Therapy Vol.3 (Bree example)"]
            },
            {
              "id": "intellectualizer",
              "name": "Intellectualizer",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Intellectualizer keeps the person in their head and away from emotional experience, using analysis, rationality, and abstraction as a shield against feeling. It may dominate conversations and IFS sessions by analyzing parts rather than connecting with them experientially. While intellectual understanding has value, this part uses it as a defense — flooding the mind with thinking to prevent the person from dropping into the body and feeling their exiles' pain. It often prefers to explain emotions rather than experience them.",
              "positive_intent": "To protect from being overwhelmed by emotional pain by staying in the safe territory of ideas and analysis.",
              "common_behaviors": ["Over-analyzing rather than feeling", "Keeping conversations intellectual", "Derailing IFS sessions with theorizing", "Difficulty accessing body-based or emotional experience"],
              "often_polarized_with": ["Emotional expression", "Exiles"],
              "exile_protected": "A child who was overwhelmed by or punished for emotional expression",
              "healthy_version": "Intellectual clarity as a service of the Self",
              "sources": ["Earley Self-Therapy"]
            },
            {
              "id": "striver",
              "name": "Striver / Striving Part",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Striver Part pushes the person toward success, accomplishment, and recognition, often in extreme or irrational ways. It may be driven by a deep need to compensate for an exile who feels worthless or deficient — if the person can achieve enough, perhaps the underlying shame will be cancelled out. The Striver often causes the person to overwork, neglect relationships, and push past reasonable limits. It is frequently polarized with a Procrastinator that it inadvertently creates by exhausting the person or by triggering fear of failure.",
              "positive_intent": "To protect from the shame of worthlessness and inadequacy by achieving enough to feel valuable and acceptable.",
              "common_behaviors": ["Overworking beyond reasonable limits", "Difficulty relaxing or celebrating achievements", "Constantly moving to the next goal", "Neglecting health and relationships in pursuit of success"],
              "often_polarized_with": ["Procrastinator", "Exhausted Part"],
              "exile_protected": "A child who was made to feel worthless, inadequate, or not good enough",
              "healthy_version": "Work Confidence capacity",
              "sources": ["Earley Self-Therapy (Bill example)", "Schwartz IFS Therapy"]
            },
            {
              "id": "closed_hearted",
              "name": "Closed-Hearted Part",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Closed-Hearted Part closes off the person's emotional experience and capacity for love, particularly in intimate relationships. It hardens the heart and creates distance so the person won't be vulnerable to being hurt, controlled, or abandoned. In the example given, a man's Closed-Hearted Part would cause him to lose interest in women when relationships became intimate and moved toward commitment, because it associated closeness with being controlled or engulfed (as had happened with his mother).",
              "positive_intent": "To protect from being hurt, controlled, engulfed, or abandoned in intimate relationships by preventing closeness.",
              "common_behaviors": ["Emotional withdrawal in intimate relationships", "Loss of interest when relationships deepen", "Difficulty being vulnerable", "Creating emotional distance at critical moments"],
              "often_polarized_with": ["Intimacy capacity", "Needy/Dependent exile"],
              "exile_protected": "A child who was controlled, hurt, or engulfed by a parent in close relationship",
              "healthy_version": "Intimacy capacity; Self-Support capacity",
              "sources": ["Earley Self-Therapy (Joe example)"]
            },
            {
              "id": "conflict_avoider",
              "name": "Conflict Avoider",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Conflict Avoider withdraws from disagreements, becomes placating, or gives in immediately in order to prevent conflict. It believes that conflict is extremely dangerous — perhaps because the person experienced explosive anger, violence, or profound emotional shutdown in their family when conflict arose. While it prevents immediate conflict, it also prevents honest communication and leads to resentment building over time, sometimes expressing itself through passive-aggressive behavior.",
              "positive_intent": "To protect from the danger of conflict escalating into violence, emotional explosion, or abandonment.",
              "common_behaviors": ["Withdrawal when tension arises", "Immediate capitulation even when the person has valid concerns", "Difficulty asserting needs", "Peace-at-any-cost approach"],
              "often_polarized_with": ["Assertiveness capacity", "Angry Part"],
              "exile_protected": "A child who was hurt by parental conflict, explosive anger, or who experienced abandonment during disagreements",
              "healthy_version": "Skillful Communication capacity; Assertiveness capacity",
              "sources": ["Earley Self-Therapy (Jim example)"]
            },
            {
              "id": "controlling_part",
              "name": "Controlling Part",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Controlling Part tries to manage, arrange, and control both the external world and the person's internal experience to prevent unexpected pain or harm. It needs certainty and predictability. In interpersonal relationships, it may tell others how they should behave, think, or feel in an attempt to create safety. The Controlling Part often sees others' autonomy or unpredictability as a threat. It is frequently polarized with a Rebel Part in oneself or in one's partner.",
              "positive_intent": "To create safety by ensuring that nothing unpredictable, dangerous, or painful can occur.",
              "common_behaviors": ["Needing to manage others' behavior", "Difficulty tolerating uncertainty", "Micromanaging situations", "Telling people how they should act or feel"],
              "often_polarized_with": ["Rebel Part", "Passive-Aggressive Part"],
              "exile_protected": "A child who felt unsafe and powerless in an unpredictable environment",
              "healthy_version": "Responsibility capacity; Assertiveness capacity",
              "sources": ["Earley Self-Therapy", "Earley Vol.3"]
            },
            {
              "id": "approval_seeker",
              "name": "Approval-Seeking Part",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Approval-Seeking Part constantly monitors others' reactions and tries to win their approval, appreciation, or admiration. It may work to make the person highly likeable, charismatic, or impressive in social situations. The underlying driver is an exile's deep belief that they are only valuable when others approve of them. This part sees a hole of deficiency inside and tries to fill it with external validation.",
              "positive_intent": "To build confidence and self-esteem through external validation, and to prevent the exile's feeling of worthlessness from being triggered by others' disapproval.",
              "common_behaviors": ["Excessive concern with others' opinions", "Adjusting behavior based on perceived reactions", "Difficulty tolerating disapproval", "Seeking praise and reassurance"],
              "often_polarized_with": ["Self-Esteem capacity"],
              "exile_protected": "A child who felt worthless or unlovable unless praised or approved of by others",
              "healthy_version": "Self-Esteem capacity",
              "sources": ["Earley Self-Therapy", "Schwartz IFS Therapy"]
            },
            {
              "id": "distancing_part",
              "name": "Distancer / Distancing Part",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Distancing Part creates emotional, physical, or relational distance to prevent the person from being hurt, abandoned, or engulfed in close relationships. It may avoid commitment, remain emotionally unavailable within relationships, or sabotage intimacy when it becomes too close for comfort. While it appears similar to the Closed-Hearted Part, the Distancer is more broadly about maintaining distance in all intimate relationships rather than specifically closing off emotional experience.",
              "positive_intent": "To protect from being hurt, abandoned, engulfed, or controlled in intimate relationships by maintaining safe distance.",
              "common_behaviors": ["Emotional unavailability", "Avoidance of commitment", "Pulling away when relationships deepen", "Preferring superficial connections"],
              "often_polarized_with": ["Dependent Part", "Intimacy capacity"],
              "exile_protected": "A child who was hurt, abandoned, or engulfed in close early relationships",
              "healthy_version": "Self-Support capacity; Intimacy capacity",
              "sources": ["Earley Self-Therapy Vol.3", "Schwartz IFS Therapy"]
            },
            {
              "id": "work_ethic_part",
              "name": "Work Ethic Part",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Work Ethic Part is a specific named manager that appeared in Nancy's case example regarding her jewelry-making business. It drove her to work constantly, feeling overwhelmed and alone with all the business responsibilities. It was deeply invested in order, planning, and productivity, and was terrified that without its vigilance everything would fall apart. It felt like the only responsible one in the system, which is a classic posture of parentified manager parts that have taken on more than they can handle.",
              "positive_intent": "To ensure success, financial stability, and meeting of external obligations; to prevent the shame and consequences of failure.",
              "common_behaviors": ["Working excessive hours", "Difficulty delegating or trusting others", "Feeling overwhelmed and alone", "Resenting parts that want rest or play"],
              "often_polarized_with": ["Procrastinator", "Kid Part"],
              "exile_protected": "An overwhelmed child who felt solely responsible for keeping things together",
              "healthy_version": "Work Confidence capacity; Ease capacity",
              "sources": ["Earley Resolving Inner Conflict (Nancy example)"]
            },
            {
              "id": "thinker_controller",
              "name": "Thinker / Controller",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Thinker or Controller is a manager type described by Schwartz in IFS Therapy. It is highly intellectual and effective at problem-solving, but also obsessively pushes feelings away and keeps the person in their head. It may be responsible for significant external achievements while simultaneously being cut off from inner emotional life. It controls the person's access to their own feelings, believing that emotional experience is dangerous or disruptive.",
              "positive_intent": "To keep the person functional, rational, and in control by suppressing emotional experience that might be overwhelming.",
              "common_behaviors": ["Living in the head; analytical approach to everything", "Blocking emotional access", "High external achievement", "Difficulty with intimate emotional connection"],
              "often_polarized_with": ["Emotional exiles", "Pleasure capacity"],
              "exile_protected": "A child who was overwhelmed by or punished for emotional experience",
              "healthy_version": "Clarity capacity; integrated intellect",
              "sources": ["Schwartz IFS Therapy"]
            },
            {
              "id": "hyperaroused_worrier",
              "name": "Hyperaroused Worrier / Sentry",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Hyperaroused Worrier or Sentry is in a constant state of alertness and vigilance, scanning the environment for any potential threat. It flashes worst-case scenarios before the person when they consider taking risks, making changes, or engaging in relationships. This part is stuck in a past where danger was pervasive and unpredictable, and hasn't updated to the relative safety of the present. It often manifests as anxiety disorders or hypervigilance.",
              "positive_intent": "To prevent the person from being caught off guard by danger by maintaining constant vigilance.",
              "common_behaviors": ["Chronic anxiety", "Catastrophic thinking", "Difficulty relaxing or trusting safety", "Scanning environment for threats"],
              "often_polarized_with": ["Calm capacity", "Trusting Part"],
              "exile_protected": "A child who grew up in an environment of real or perceived danger, unpredictability, or threat",
              "healthy_version": "Calm capacity; appropriate perceptiveness",
              "sources": ["Schwartz IFS Therapy"]
            },
            {
              "id": "pessimist_manager",
              "name": "Pessimist Manager",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Pessimist Manager is a specific manager type described by Schwartz that is distinct from the Depressing Protector. Rather than primarily causing depression, it focuses on undermining the person's confidence to keep them from trying things that might lead to disappointment. It gives the person the sense that they can't succeed, people won't like them, and things won't work out. By lowering expectations proactively, it tries to prevent the devastation of failure.",
              "positive_intent": "To protect the person from the pain of failure and disappointment by ensuring they don't try things that could go wrong.",
              "common_behaviors": ["Persistent negative predictions", "Undermining confidence before attempts", "Finding reasons why things won't work", "Eroding self-belief"],
              "often_polarized_with": ["Striving Part", "Optimistic capacity"],
              "exile_protected": "A child who was devastated by failure or whose hopes were repeatedly crushed",
              "healthy_version": "Appropriate prudence; realistic optimism",
              "sources": ["Schwartz IFS Therapy"]
            },
            {
              "id": "dependent_manager",
              "name": "Dependent Manager",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Dependent Manager keeps the person appearing helpless, injured, or passive as a way of ensuring that other people will take care of them. It has learned that neediness and vulnerability are effective strategies for obtaining care and support. By presenting as unable to manage, this part recruits others into a caretaking role. It often creates a false presentation of helplessness that may or may not reflect the person's actual capabilities.",
              "positive_intent": "To ensure the person's needs are met and they are cared for by maintaining a position of apparent helplessness or neediness.",
              "common_behaviors": ["Understating capabilities to others", "Creating or amplifying a sense of being overwhelmed", "Recruiting others into caretaking roles", "Difficulty expressing actual competence"],
              "often_polarized_with": ["Self-Support capacity", "Assertiveness capacity"],
              "exile_protected": "A child who only received care when appearing helpless or needy",
              "healthy_version": "Self-Support capacity; authentic vulnerability",
              "sources": ["Schwartz IFS Therapy"]
            },
            {
              "id": "denier",
              "name": "Denier",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Denier distorts the person's perception of reality to protect them from seeing threatening or painful truths. It may minimize, rationalize, or simply block the person's awareness of problems in their life, relationships, or behavior. While it intends to protect, the Denier ultimately keeps the person from being able to respond appropriately to real challenges. It is often heavily involved in addiction, abusive relationships, and self-destructive patterns.",
              "positive_intent": "To protect the person from having to face painful or threatening realities that feel overwhelming.",
              "common_behaviors": ["Minimizing serious problems", "Rationalizing harmful behavior", "Difficulty acknowledging the impact of one's actions", "Refusing to see what is obvious to others"],
              "often_polarized_with": ["Truth-facing capacity", "Responsible acknowledgment"],
              "exile_protected": "A child who couldn't tolerate the full reality of their circumstances",
              "healthy_version": "Honest awareness; appropriate reality contact",
              "sources": ["Schwartz IFS Therapy"]
            },
            {
              "id": "spacer",
              "name": "Spacer",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Spacer (named in Bree's case example) is a specific dissociative manager that causes the person to space out, become foggy, or disconnect from immediate experience when the intensity of exile pain threatens to surface. It is distinct from the Foggy Part in that the Spacer arises specifically to prevent exile overwhelm in the moment of IFS work, while the Foggy Part has a broader function. The Spacer intervenes to preserve the person's ability to function by preventing flooding.",
              "positive_intent": "To prevent the person from being overwhelmed by intense exile pain by dissociating from the present moment.",
              "common_behaviors": ["Suddenly becoming foggy or disconnected during IFS sessions", "Difficulty staying present when emotional intensity rises", "Losing the thread of work when approaching exiles"],
              "often_polarized_with": ["Aliveness capacity", "Presence"],
              "exile_protected": "A deeply wounded child carrying intense trauma or pain",
              "healthy_version": "Grounded presence; ability to stay with difficult emotions",
              "sources": ["Earley Self-Therapy Vol.3 (Bree example)"]
            },
            {
              "id": "foggy_part",
              "name": "Foggy Part",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Foggy Part causes the person to lose conscious awareness of themselves, their thought processes, and their connection to their body. When active, the person may feel spaced out, sleepy, dull, confused, or overwhelmed. In the context of eating issues, the Foggy Part often allies with the Indulger to enable unconscious eating by disconnecting the person from awareness of what and how much they are consuming. More broadly, it can block any attempt at self-awareness or change by making it impossible to think clearly.",
              "positive_intent": "To protect from being overwhelmed by painful feelings or self-awareness by clouding consciousness; to prevent change that feels threatening.",
              "common_behaviors": ["Dissociation during emotional moments", "Unconscious eating or other behaviors", "Difficulty thinking clearly about personal issues", "Sudden loss of focus during self-reflection"],
              "often_polarized_with": ["Conscious Consumption capacity", "Clarity"],
              "exile_protected": "Exiles carrying overwhelming pain or shame",
              "healthy_version": "Clear awareness; mindful presence",
              "sources": ["Earley Self-Therapy Vol.3"]
            },
            {
              "id": "drink_controller",
              "name": "Drink Controller",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Drink Controller is a specific named manager in Dan's case example from Resolving Inner Conflict. It tries to limit or prevent alcohol consumption, typically by shaming the person after drinking and trying to impose limits. It is intensely polarized with the Drinker Part (a firefighter), believing that the Drinker's behavior is causing serious harm to the person's life. Like all Inner Controllers, its strategy of shame and restriction tends to backfire, making the exile's pain worse and the Drinker more reactive.",
              "positive_intent": "To protect the person from the physical, relational, and social harms of excessive drinking.",
              "common_behaviors": ["Shaming and criticizing after drinking", "Attempting to impose rigid drinking rules", "Creating intense self-loathing around alcohol use", "Engaging in constant battle with the Drinker Part"],
              "often_polarized_with": ["Drinker Part"],
              "exile_protected": "Exiles who feel ashamed when Dan gets drunk or who fear abandonment due to relationship damage",
              "healthy_version": "Conscious Consumption capacity; Restraint capacity",
              "sources": ["Earley Resolving Inner Conflict (Dan example)"]
            },
            {
              "id": "passive_aggressive_part",
              "name": "Passive-Aggressive Part",
              "category": "protector",
              "subcategory": "manager",
              "description": "The Passive-Aggressive Part expresses resentment and rebellion indirectly and unconsciously, while the person consciously presents as agreeable and cooperative. It arises when direct expression of anger or assertion is blocked by a People-Pleasing Part. Unable to express defiance directly, this part acts out its anger through indirect means: forgetting commitments, doing tasks improperly, small sabotages, and other behaviors that frustrate and hurt the other person while maintaining plausible deniability. It is often completely unconscious.",
              "positive_intent": "To express resentment and preserve autonomy when direct assertion feels too dangerous; to get revenge for feeling controlled or dismissed.",
              "common_behaviors": ["'Forgetting' commitments", "Doing tasks incorrectly or incompletely", "Subtle sabotages", "Indirect expressions of anger that leave the person feeling confused and frustrated"],
              "often_polarized_with": ["People-Pleasing Part", "Assertiveness capacity"],
              "exile_protected": "A child who couldn't directly express anger or dissent without being punished",
              "healthy_version": "Assertiveness capacity; Cooperation capacity",
              "sources": ["Earley Self-Therapy Vol.3"]
            }
          ]
        }
      },
      "firefighters": {
        "description": "Firefighters are reactive protectors that jump in after an exile's pain has been triggered, attempting to suppress, drown out, distract from, or numb the exile's emotions. They tend to be impulsive and willing to ignore consequences in order to stop the emotional 'fire' of exile pain as quickly as possible. While they often cause significant external harm, their intent is always to protect the person from what they believe would be an unbearable emotional experience.",
        "parts": [
          {
            "id": "drinker",
            "name": "Drinker / Alcohol Part",
            "category": "protector",
            "subcategory": "firefighter",
            "description": "The Drinker Part uses alcohol to suppress, numb, or distract from exile pain that has been activated. It turns to alcohol as a reliable, fast-acting way to make the underlying pain tolerable. In Dan's case, the Drinker was protecting a young exile wounded by his mother's rejection. The Drinker believed that the exile's pain was intolerable and that alcohol was the only reliable solution. It had no idea that its strategy was creating additional problems, including threatening Dan's marriage.",
            "positive_intent": "To suppress or numb exile pain that feels unbearable, providing temporary relief.",
            "common_behaviors": ["Drinking to excess when emotionally triggered", "Using alcohol to numb or escape feelings", "Escalating alcohol use when exile pain intensifies"],
            "often_polarized_with": ["Drink Controller"],
            "exile_protected": "A child deeply wounded by rejection, abandonment, or emotional unavailability",
            "healthy_version": "Appropriate use of pleasure; capacity to feel and process emotions",
            "sources": ["Earley Resolving Inner Conflict (Dan example)"]
          },
          {
            "id": "indulger",
            "name": "Indulger / Overeater",
            "category": "protector",
            "subcategory": "firefighter",
            "description": "The Indulger uses food (or sometimes other substances or activities) to soothe, comfort, numb, or distract from exile pain. It may be responding to emotional hunger, loneliness, shame, fear, or grief. The Indulger may have learned in infancy or early childhood that food provides comfort and fills emptiness, making it the go-to solution for any emotional distress. It often operates unconsciously, with the person going on 'autopilot' while eating, enabled by the Foggy Part. The Indulger is not simply an 'eating problem' — it is a compassionate (if flawed) attempt to protect deeply wounded parts.",
            "positive_intent": "To soothe, numb, and comfort exiles in pain; to fill inner emptiness; to provide pleasure as an antidote to suffering.",
            "common_behaviors": ["Binge eating when emotionally triggered", "Unconscious or compulsive eating", "Eating past fullness", "Thinking about the next food while eating the current one"],
            "often_polarized_with": ["Food Controller", "Rebel"],
            "exile_protected": "Deprived, lonely, or shamed child parts; exiles carrying fear or grief",
            "healthy_version": "Pleasure capacity; Conscious Consumption capacity",
            "sources": ["Earley Self-Therapy Vol.3"]
          },
          {
            "id": "angry_part",
            "name": "Angry Part / Enraged Part",
            "category": "protector",
            "subcategory": "firefighter",
            "description": "The Angry Part uses rage and anger to protect exiles from external threat or to distract from and cover their emotional pain. Protector anger can serve two main functions: external protection (keeping threatening people away or fighting against domination) and internal distraction (replacing the exile's vulnerable pain with anger, which feels more powerful). When a person has disowned their anger, this part may be hidden and expressed only in passive-aggressive ways or occasional explosive outbursts. When it is acted out, it is often more intense than the situation warrants because it is being fueled by old exile wounds.",
            "positive_intent": "To protect vulnerable exiles from being hurt again by others, or to distract the person from intolerable exile pain by substituting anger.",
            "common_behaviors": ["Anger that is disproportionate to situations", "Rage when vulnerability is triggered", "Using anger to maintain emotional distance", "Explosive outbursts after suppression"],
            "often_polarized_with": ["Inner Controller", "Disowned Anger", "People-Pleasing Part"],
            "exile_protected": "A child who was hurt, controlled, or dominated; also protects against the pain of rejection, abandonment, or worthlessness",
            "healthy_version": "Strength capacity; Restraint capacity",
            "sources": ["Earley Self-Therapy Vol.3", "Earley Self-Therapy", "Schwartz IFS Therapy"]
          },
          {
            "id": "dissociative_part",
            "name": "Dissociative Part",
            "category": "protector",
            "subcategory": "firefighter",
            "description": "The Dissociative Part removes the person from conscious experience when exile pain threatens to overwhelm them. It may cause the person to feel unreal, detached, foggy, or as if watching themselves from outside. In extreme cases, it can cause significant disconnection from reality. Schwartz notes that in people with severe trauma histories, dissociative parts can be particularly prominent, using amnesic barriers to prevent overwhelming exiles from surfacing. This was actually the mechanism by which the Self was originally pushed out of the body during trauma.",
            "positive_intent": "To protect the person (and the Self) from being overwhelmed or destroyed by the intensity of traumatic exile emotions.",
            "common_behaviors": ["Depersonalization and derealization", "Memory gaps", "Feeling disconnected from the body", "Sudden fogginess or unreality when emotional topics arise"],
            "often_polarized_with": ["Embodied presence", "Aliveness capacity"],
            "exile_protected": "Traumatized child parts carrying terror, shame, or helplessness",
            "healthy_version": "Grounded embodied presence",
            "sources": ["Schwartz IFS Therapy"]
          },
          {
            "id": "cutter_self_harmer",
            "name": "Cutter / Self-Harming Part",
            "category": "protector",
            "subcategory": "firefighter",
            "description": "The Cutter or Self-Harming Part uses physical pain or injury to manage emotional pain. In Roxanne's pivotal case example, the Cutting Part initially appeared to be simply destructive, but when Schwartz stopped trying to coerce it and became genuinely curious, it revealed its heroic history: it had protected Roxanne during childhood abuse by taking her out of her body and controlling her rage (which would have endangered her further). It was not a pathological impulse but a part that had once saved her life, now stuck in an outdated strategy.",
            "positive_intent": "Originally: to take the person out of their body during abuse and control dangerous rage. In the present: to manage unbearable emotional pain through physical sensation; to create a sense of control over one's experience.",
            "common_behaviors": ["Self-cutting or other self-harm", "Using physical pain to regulate overwhelming emotional states", "A sense of relief or release through self-harm"],
            "often_polarized_with": ["Managers who hate this behavior"],
            "exile_protected": "A child who was physically or sexually abused; also protects against overwhelming rage and shame",
            "healthy_version": "Embodied aliveness; appropriate self-regulation",
            "sources": ["Schwartz IFS Therapy (Roxanne example)"]
          },
          {
            "id": "rebel_part",
            "name": "Rebel Part",
            "category": "protector",
            "subcategory": "firefighter",
            "description": "The Rebel Part defies rules, authority, and control — both external and internal — as a way of preserving the person's sense of autonomy and freedom. In eating contexts, the Rebel specifically fights against the Food Controller, bingeing as an act of defiance when told what to eat. More broadly, the Rebel has learned that if it doesn't fight back against controlling forces, the person will be completely dominated. Like a teenager asserting independence, it often goes too far, causing harm in its pursuit of freedom.",
            "positive_intent": "To preserve the person's autonomy and freedom from domination, both by inner critics and by controlling external figures.",
            "common_behaviors": ["Doing the opposite of what is demanded", "Deliberate violation of rules it finds oppressive", "Acting out when controlled", "Gaining satisfaction from defiance"],
            "often_polarized_with": ["Controlling Part", "Food Controller", "Taskmaster"],
            "exile_protected": "A child who was dominated, controlled, or had their autonomy crushed",
            "healthy_version": "Assertiveness capacity; healthy individuality",
            "sources": ["Earley Self-Therapy Vol.3", "Schwartz IFS Therapy"]
          },
          {
            "id": "inner_rebel",
            "name": "Inner Rebel",
            "category": "protector",
            "subcategory": "firefighter",
            "description": "The Inner Rebel is specifically oriented toward defying the person's own inner authority figures — particularly Inner Critics. When a Critic tells the person what they should or shouldn't do, the Inner Rebel refuses to comply as a way of protecting the person's sense of inner freedom. While the Rebel fights external controllers, the Inner Rebel specifically pushes back against internal ones. This can undermine healthy disciplines like exercise, meditation, or eating well when those feel 'imposed' rather than chosen.",
            "positive_intent": "To prevent the person from being dominated by their own inner critical voices and to preserve a sense of internal freedom.",
            "common_behaviors": ["Refusing to follow healthy routines that feel 'forced'", "Doing the opposite of what the Inner Critic demands", "Sabotaging positive changes that feel imposed rather than chosen"],
            "often_polarized_with": ["Inner Critic", "Taskmaster", "Perfectionist"],
            "exile_protected": "A child whose inner life was controlled and dominated by critical parents",
            "healthy_version": "Assertiveness capacity; healthy self-determination",
            "sources": ["Earley Self-Therapy Vol.3"]
          },
          {
            "id": "procrastinator",
            "name": "Procrastinator",
            "category": "protector",
            "subcategory": "firefighter",
            "description": "The Procrastinator avoids tasks that feel threatening, particularly those involving evaluation, judgment, or the possibility of failure. It does not simply avoid work out of laziness — it avoids the emotional risk that comes with trying and potentially failing or being judged. By not starting a task, the Procrastinator protects the person from ever having to face the exile's fear of failure, humiliation, or rejection. It may also be rebelling against a dominating Taskmaster, taking the freedom it needs in the only way available to it.",
            "positive_intent": "To protect the person from the pain of potential failure, judgment, humiliation, or rejection by avoiding the task altogether; may also be preserving autonomy against the Taskmaster.",
            "common_behaviors": ["Avoiding important tasks", "Getting distracted with less important activities", "Forgetting tasks that feel threatening", "Difficulty getting started on anything evaluative"],
            "often_polarized_with": ["Taskmaster", "Perfectionist"],
            "exile_protected": "A child who was judged, humiliated, or shamed for failures or imperfect performance",
            "healthy_version": "Work Confidence capacity; Ease capacity",
            "sources": ["Earley Self-Therapy Vol.3", "Earley Self-Therapy (Sandy example)"]
          },
          {
            "id": "busy_part",
            "name": "Busy Part",
            "category": "protector",
            "subcategory": "firefighter",
            "description": "The Busy Part keeps the person occupied with other activities — cleaning, exercise, cooking, browsing — as a way of distracting from something threatening that they need to face. In Sandy's example, the Busy Part kept her busy with household tasks and workouts to prevent her from working on an important creative project that her Embarrassed Child Part feared would expose her to ridicule. The Busy Part operates by making distracting activities feel more urgent or appealing than the feared task.",
            "positive_intent": "To protect from the threat of visibility, judgment, or failure by keeping the person too occupied to engage with what is feared.",
            "common_behaviors": ["Compulsive busyness with secondary tasks", "Finding an endless supply of 'urgent' distractions", "Inability to settle into the important thing", "Activity that looks productive but avoids the actual priority"],
            "often_polarized_with": ["Pushy/Critical Part", "Work Confidence capacity"],
            "exile_protected": "A child who was ridiculed or shamed for being publicly visible",
            "healthy_version": "Appropriate prioritization; Work Confidence capacity",
            "sources": ["Earley Self-Therapy (Sandy example)"]
          }
        ]
      }
    },
    "exiles": {
      "description": "Exiles are young child parts that are carrying pain, fear, shame, or trauma from the past. They have been pushed out of consciousness by protectors because their emotions felt too overwhelming or dangerous to feel. Exiles exist in a kind of frozen present, often stuck at the age when the wounding occurred, unaware that the person has grown up. They long to be seen, understood, and healed, but their desperation for connection and their intensity of feeling can frighten protective parts.",
      "parts": [
        {
          "id": "frightened_child",
          "name": "Frightened Child / Scared Kid",
          "category": "exile",
          "description": "The Frightened Child is one of the most common exile types, carrying the burden of fear from early experiences of danger, threat, abuse, or unpredictability. This part is often accessed when a Critic or Attacker loosens its grip and reveals the terrified child underneath. In Sarah's case, the Scared Kid was the exile that her massive Attacker part was actually protecting — by attacking Sarah itself, the Attacker prevented her parents from doing worse. The Frightened Child often feels frozen in the dangerous moment in which it was first terrified.",
          "burden": "Pervasive fear; terror; sense of being in constant danger",
          "typical_origins": "Childhood abuse, violence, unpredictable caregivers, witnessing traumatic events",
          "common_expressions": "Anxiety, hypervigilance, panic attacks, terror when triggered",
          "sources": ["Earley Self-Therapy Vol.3 (Sarah example)", "Multiple sources"]
        },
        {
          "id": "criticized_child",
          "name": "Criticized Child",
          "category": "exile",
          "description": "The Criticized Child is the exile who directly receives and believes the Inner Critic's attacks. It feels the shame, inadequacy, and worthlessness that the Critic promotes. This part not only feels bad in the moment of criticism but has organized its entire self-concept around the Critic's messages — it genuinely believes it is the loser, failure, or worthless person the Critic says it is. Healing the Criticized Child requires demonstrating, through the Self's love and acceptance, that the Critic's judgments are not the truth of who the person is.",
          "burden": "Deep shame; sense of worthlessness; inadequacy; self-doubt",
          "typical_origins": "Being repeatedly criticized, judged, or shamed by parents, teachers, or peers",
          "common_expressions": "Chronic shame; low self-esteem; accepting criticism as truth; depression",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "protected_child",
          "name": "Protected Child",
          "category": "exile",
          "description": "The Protected Child is the exile that the Inner Critic is actually trying to protect — which may or may not be the same as the Criticized Child. In some cases the Critic is simultaneously protecting and harming the same child exile. In other cases, the Critic attacks one exile (the Criticized Child) in order to protect a different, deeper exile (the Protected Child) from external danger. Understanding which exile is being protected is crucial for fully resolving the Inner Critic's role, as the Critic will not fully let go until the Protected Child is healed.",
          "burden": "Varies by type: fear of attack, humiliation, abandonment, being controlled, etc.",
          "typical_origins": "Specific childhood traumas that the Critic formed around protecting against",
          "common_expressions": "The exile's particular pain that the Critic is guarding against",
          "sources": ["Earley Self-Therapy Vol.3 (Annie example)"]
        },
        {
          "id": "deprived_child",
          "name": "Deprived Child / Deprived Part",
          "category": "exile",
          "description": "The Deprived Child is an exile that didn't receive enough nurturing, caring, love, holding, or attunement in early childhood. It carries a deep inner emptiness and longing for what was missing. This part often corresponds to what developmental psychology calls 'insecure attachment.' The Deprived Child feels fundamentally alone, uncared-for, and as if no one will ever truly be there for it. It may desperately seek fulfillment through relationships, food, substances, or other external sources, never quite finding the satisfaction it seeks because only the Self's direct attention can truly address this wound.",
          "burden": "Inner emptiness; profound loneliness; desperate need for nurturing and love; feeling fundamentally uncared-for",
          "typical_origins": "Emotional neglect; inconsistent caregiving; insecure early attachment; deprivation of physical affection",
          "common_expressions": "Dependent patterns in relationships; using food or substances to fill emptiness; chronic longing; depression",
          "sources": ["Earley Self-Therapy", "Schwartz IFS Therapy"]
        },
        {
          "id": "abandoned_child",
          "name": "Abandoned Child",
          "category": "exile",
          "description": "The Abandoned Child is an exile that experienced being left, given up on, or losing a caregiver in childhood. This part carries a terror of being abandoned again and often sees abandonment in situations where others might not. It can make the person cling desperately to relationships or, conversely, prevent them from forming close attachments at all (as a different kind of protection). The Abandoned Child typically believes that abandonment is inevitable and that it fundamentally deserves to be left.",
          "burden": "Terror of abandonment; sense that being left is inevitable; feeling unworthy of being stayed for",
          "typical_origins": "Parental abandonment, death, divorce, hospitalization; inconsistent emotional availability; being 'given up on' by caregivers",
          "common_expressions": "Abandonment fears in relationships; difficulty tolerating separation; panic when partners need space; or avoidance of attachment",
          "sources": ["Schwartz IFS Therapy", "Earley Self-Therapy"]
        },
        {
          "id": "rejected_child",
          "name": "Rejected Child",
          "category": "exile",
          "description": "The Rejected Child is an exile that was rejected when it reached out for connection — whether that rejection was explicit (being told to go away) or implicit (consistent emotional unavailability). This part carries the pain of reaching out and being turned away, and often concludes that something is fundamentally wrong with it — that it is unlovable or unwanted. It may become hypersensitive to any hint of rejection in the present, triggering protectors to act defensively before rejection can occur.",
          "burden": "Pain of being turned away; belief that reaching out is dangerous; feeling unlovable or unwanted",
          "typical_origins": "Parental rejection, emotional unavailability, peer exclusion, being explicitly told one is unwanted",
          "common_expressions": "Hypersensitivity to perceived rejection; avoidance of reaching out; hypervigilance to others' reactions",
          "sources": ["Earley Self-Therapy Vol.3", "Schwartz IFS Therapy"]
        },
        {
          "id": "humiliated_child",
          "name": "Humiliated Child",
          "category": "exile",
          "description": "The Humiliated Child is an exile that was publicly shamed, ridiculed, or embarrassed in childhood — by parents, siblings, peers, or teachers. It carries the burning shame of having been exposed as inadequate, ridiculous, or worthless in front of others. This part often drives a terror of visibility: being seen, performing, speaking up, or being in the spotlight. The Humiliated Child frequently works in concert with a Perfectionist or Underminer Critic that tries to prevent future humiliation by ensuring the person is either perfect or invisible.",
          "burden": "Burning shame; terror of being exposed or ridiculed; sense of being fundamentally ridiculous or inadequate",
          "typical_origins": "Being mocked or laughed at in childhood; being publicly shamed by parents or teachers; peer bullying",
          "common_expressions": "Social anxiety; fear of public speaking or performance; terror of being seen; shame attacks",
          "sources": ["Earley Self-Therapy", "Schwartz IFS Therapy"]
        },
        {
          "id": "worthless_child",
          "name": "Worthless Child",
          "category": "exile",
          "description": "The Worthless Child carries the burden of believing it has no intrinsic value — that it is fundamentally defective, bad, or simply not worth caring about. This burden was typically installed through repeated messages, explicit or implicit, that the child didn't measure up, wasn't good enough, or was a disappointment. In IFS, worthlessness is understood as a burden — not an intrinsic quality of the part — which is why it can be unburdened and released through the healing process. Bill's 'Little Billy' is a clear example of this exile type.",
          "burden": "Deep belief in own worthlessness; sense of being fundamentally unacceptable or not good enough",
          "typical_origins": "Being told one is worthless; chronic criticism and non-validation; being compared unfavorably to others; being told one is a disappointment",
          "common_expressions": "Low self-esteem; depression; inability to take in praise; feeling like a fraud; overworking to compensate",
          "sources": ["Earley Self-Therapy (Bill/Little Billy example)"]
        },
        {
          "id": "ashamed_exile",
          "name": "Ashamed Exile",
          "category": "exile",
          "description": "The Ashamed Exile is broader than the Worthless Child and carries a deep sense of being fundamentally flawed, damaged, or defective. Shame as a burden tells the person that they are inherently bad (rather than that they did something bad). This exile often hides and doesn't want to be seen precisely because its core fear is that if anyone truly saw it, they would be revolted or would leave. The Ashamed Exile is extremely common and is at the root of many protective patterns.",
          "burden": "Shame; sense of being fundamentally defective, damaged, or disgusting; belief that one must hide who one truly is",
          "typical_origins": "Sexual abuse; severe emotional abuse; repeated shaming; being treated as disgusting or unacceptable",
          "common_expressions": "Hiding, concealment, fear of exposure; perfectionism to cover up the 'flaw'; depression; difficulty with intimacy",
          "sources": ["Schwartz IFS Therapy", "Multiple sources"]
        },
        {
          "id": "unlovable_exile",
          "name": "Unlovable Exile",
          "category": "exile",
          "description": "The Unlovable Exile carries the conviction that it is fundamentally unlovable — that no one could truly love them if they really knew them. This belief typically developed in response to experiences of neglect, rejection, or conditional love where the child concluded 'I am not being loved because there is something wrong with me.' This exile often drives relationships in profound ways: desperately seeking love while simultaneously believing it will never come or won't last.",
          "burden": "Belief that one is fundamentally unlovable; conviction that love will always be withdrawn or was never real",
          "typical_origins": "Emotional neglect; conditional love; repeated experiences of not being valued for who one is",
          "common_expressions": "Desperate relationship seeking; inability to believe in love; testing relationships; pushing people away while fearing abandonment",
          "sources": ["Schwartz IFS Therapy", "Earley Self-Therapy"]
        },
        {
          "id": "needy_exile",
          "name": "Needy Part",
          "category": "exile",
          "description": "The Needy Part is an exile that carries intense, unmet developmental needs for love, nurturing, attention, and connection. Because these needs went unmet in childhood, they have built up enormous pressure and drive. When activated, the Needy Part can overwhelm the person with longing and can cause them to pursue connection in desperate, clinging ways. Protectors often work overtime to either keep this part hidden (for fear of driving others away) or to find external sources of fulfillment for its needs.",
          "burden": "Intense, pressing need for love and connection; sense of being insatiably hungry for nurturance; feeling like needs are shameful or too much",
          "typical_origins": "Emotional deprivation; caregivers who were unavailable, neglectful, or inconsistent; not having needs met in early development",
          "common_expressions": "Clingy or dependent behavior in relationships; using food, substances, or other external sources to fill neediness; fear of being alone",
          "sources": ["Schwartz IFS Therapy", "Earley Self-Therapy"]
        },
        {
          "id": "little_girl_little_boy",
          "name": "Little Girl / Little Boy",
          "category": "exile",
          "description": "This is a generic category referring to a young child exile stuck at a specific age in a specific situation. In IFS sessions, exiles often present visually as a child of a particular age in a specific scene or situation. When working with an exile, the person may encounter 'a little girl of 5 in a dark room' or 'a boy of 7 at the kitchen table.' This part is literally experienced as being that age, in that time, with the full emotional weight of what was happening then. IFS work involves going back to that scene and providing what was needed.",
          "burden": "Varies by individual history; typically fear, shame, loneliness, worthlessness, or grief from a specific period or incident",
          "typical_origins": "A specific traumatic or wounding incident or period in childhood",
          "common_expressions": "The emotional experience of that specific time; flashbacks or intrusive memories of the period",
          "sources": ["Multiple sources throughout all texts"]
        },
        {
          "id": "baby_part",
          "name": "Baby Part",
          "category": "exile",
          "description": "The Baby Part is an extremely young exile, often preverbal, carrying wounds from the earliest period of life — infancy or toddlerhood. Because this part is so young, it typically cannot communicate in words and must be accessed through body sensations, physical feelings, and images. In Christine's case, the Baby had been left unattended in a crib, and this preverbal experience of desperate crying with no response had left a profound wound. The Baby Part often carries some of the most fundamental wounds around basic safety, lovability, and whether the world responds to one's needs.",
          "burden": "Preverbal experience of abandonment, neglect, or terror; fundamental wounds around being responded to and cared for",
          "typical_origins": "Early neglect, schedule feeding, prolonged hospital stays, maternal depression in infancy, early trauma",
          "common_expressions": "Preverbal distress; deep existential loneliness; physical holding and rocking needed; panic in abandonment situations",
          "sources": ["Earley Self-Therapy (Christine example)", "Earley Self-Therapy Vol.3 (Claire example)"]
        },
        {
          "id": "embarrassed_child",
          "name": "Embarrassed Child",
          "category": "exile",
          "description": "The Embarrassed Child is an exile that was ridiculed by peers specifically for qualities that are actually gifts — sensitivity, creativity, intelligence, expressiveness, or difference. In the example given, Sandy's Embarrassed Child had been ridiculed for being 'too sensitive' by her peers. The result was that now, whenever she attempted to be visible or make a contribution, this exile was triggered, and a Busy Part arose to protect it by keeping her from being seen. The core wound is having a genuine quality shamed rather than celebrated.",
          "burden": "Shame specifically about one's gifts, sensitivity, or unique qualities; terror of being seen and ridiculed again",
          "typical_origins": "Peer bullying or ridicule specifically for qualities that are actually strengths; parental shaming of authentic expression",
          "common_expressions": "Hiding gifts and talents; fear of visibility; block on creative expression; difficulty being seen",
          "sources": ["Earley Self-Therapy (Sandy example)"]
        },
        {
          "id": "abused_exile",
          "name": "Abused Exile",
          "category": "exile",
          "description": "The Abused Exile carries the direct wounds of physical, sexual, or severe emotional abuse. This is often the most deeply protected exile in a person's system, surrounded by the most extreme protectors. The Abused Exile typically believes it deserved the abuse (a common conclusion of child thinking) and may feel deep shame about what happened to it. It is frozen in the time of the abuse, often experiencing intense fear, powerlessness, and the sense that the abuser could return at any moment.",
          "burden": "Terror; powerlessness; shame about the abuse; belief that it was deserved; deep wound to basic safety and trust",
          "typical_origins": "Physical abuse, sexual abuse, severe emotional abuse, witnessing violence",
          "common_expressions": "PTSD symptoms; hypervigilance; difficulty trusting; body-based trauma responses; shame",
          "sources": ["Schwartz IFS Therapy", "Earley Self-Therapy Vol.3"]
        },
        {
          "id": "powerless_exile",
          "name": "Powerless / Helpless Exile",
          "category": "exile",
          "description": "The Powerless Exile carries the burden of having felt completely helpless and without agency in childhood — unable to stop what was happening, unable to get help, unable to make anyone respond. This sense of total powerlessness can be more traumatic than the specific events themselves. The Powerless Exile often leads to protectors that are intensely controlling (trying to ensure powerlessness never happens again) or deeply despairing (expecting that powerlessness is the permanent condition).",
          "burden": "Helplessness; sense of having no agency; inability to affect one's circumstances; deep passivity",
          "typical_origins": "Situations of true helplessness: abuse with no way out, neglect with no one to turn to, being completely controlled",
          "common_expressions": "Learned helplessness; depression; difficulty taking effective action; alternating between controlling behavior and collapse",
          "sources": ["Schwartz IFS Therapy"]
        },
        {
          "id": "lonely_exile",
          "name": "Lonely Exile",
          "category": "exile",
          "description": "The Lonely Exile is an exile that carries profound isolation — a deep aloneness that feels existential rather than circumstantial. This part may have been physically present with others but fundamentally unseen, unmet, or disconnected from them. In Jay Earley's personal example, his own Deprived Child was left alone in an incubator for weeks as a premature infant, and this created a Lonely Exile that was triggered every time his wife was away. The Lonely Exile's healing often requires the Self to genuinely show up as a consistent, caring companion.",
          "burden": "Profound aloneness; feeling unseen and unmet; belief that genuine connection is unavailable",
          "typical_origins": "Emotional isolation despite physical presence; early separations; caregivers who were physically present but emotionally absent",
          "common_expressions": "Depression and emptiness; desperate relationship seeking; inability to be alone; or profound withdrawal",
          "sources": ["Earley Self-Therapy (Jay's personal example)"]
        },
        {
          "id": "guilty_exile",
          "name": "Guilty Child",
          "category": "exile",
          "description": "The Guilty Child is an exile that was made to feel responsible for things that were not its fault — particularly for a parent's emotions, the family's problems, or traumatic events. Children have a developmental tendency toward self-referential thinking ('if something bad happened, it must be because of me'), and caregivers can exploit or unintentionally reinforce this. This exile carries heavy, chronic guilt and may feel fundamentally responsible for others' suffering. It often creates the Guilt Tripper Critic as its protector.",
          "burden": "Chronic guilt; feeling responsible for others' pain; belief that one's existence causes harm",
          "typical_origins": "Being made to feel responsible for parental emotions; being blamed for family problems; parentification",
          "common_expressions": "Excessive guilt; caretaking behavior; difficulty receiving without feeling obligated; depression",
          "sources": ["Schwartz IFS Therapy"]
        },
        {
          "id": "angry_exile",
          "name": "Angry Exile",
          "category": "exile",
          "description": "The Angry Exile is an exile that carries righteous rage about what was done to it — the injustice of its treatment, the harm it suffered, the ways its needs were ignored or its dignity was violated. This is distinct from protector anger, which serves a defensive function. Exile anger is a natural, valid emotional response to having been mistreated. In IFS exile work, it is important to encourage and witness this anger fully, as it is part of the exile's story and often needs to be expressed before the exile can unburden its pain.",
          "burden": "Suppressed righteous rage about past injustice and harm",
          "typical_origins": "Any childhood experience involving mistreatment, injustice, or violation",
          "common_expressions": "Appears during exile witnessing work; may show up as sudden anger that seems disconnected from present circumstances",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "kid_part",
          "name": "Kid Part",
          "category": "exile",
          "description": "The Kid Part, in Nancy's case example, was a spontaneous, playful, creative part that wanted to live freely, follow impulses, explore, and have fun — without schedules, plans, or the pressure of work. It had been exiled by the Work Ethic Part, which saw its spontaneous nature as a threat to getting things done. The Kid Part represents the natural aliveness and creativity that children have before it is socialized out of them. When exiled, this energy becomes a source of passive resistance and procrastination.",
          "burden": "Suppression of natural spontaneity and aliveness; longing for freedom and play",
          "typical_origins": "Environments where play, spontaneity, and impulsiveness were controlled or punished",
          "common_expressions": "Shows up as procrastination; daydreaming; difficulty settling to work; passive resistance to structure",
          "sources": ["Earley Resolving Inner Conflict (Nancy example)"]
        }
      ]
    },
    "healthy_parts_and_capacities": {
      "description": "Healthy parts and capacities are parts in non-extreme, constructive roles — either parts that have never taken on burdens or parts that have been transformed through IFS work. In IFS, after exiles are unburdened and protectors are released from their extreme roles, they can manifest their natural, healthy qualities. Healthy capacities can also be actively developed and cultivated.",
      "parts": [
        {
          "id": "inner_champion",
          "name": "Inner Champion",
          "category": "healthy_capacity",
          "description": "The Inner Champion is an aspect of the Self identified by Bonnie Weiss and Jay Earley that supports, encourages, and advocates for the person in the face of Inner Critic attacks. It is like the ideal supportive parent the person always wished they had — one who sees their worth clearly, believes in them unconditionally, and helps them feel good about themselves not through fighting the Critic but through genuine affirmation and acceptance. The Inner Champion doesn't argue with the Critic; it simply offers a different, truer perspective. Each type of Inner Critic has a corresponding Inner Champion that speaks specifically to its particular attacks.",
          "qualities": ["Unconditional acceptance", "Encouragement", "Genuine affirmation of worth", "Protection from Critic attacks without fighting them"],
          "healthy_version_of": "Inner Defender",
          "transforms": "Inner Critic",
          "sources": ["Earley Self-Therapy Vol.3", "Earley Freedom from Your Inner Critic"]
        },
        {
          "id": "inner_mentor",
          "name": "Inner Mentor",
          "category": "healthy_capacity",
          "description": "The Inner Mentor is the healthy version of the Inner Critic — a wise, caring inner voice that performs the genuine self-evaluation function in a supportive rather than punishing way. It helps the person see clearly when their behavior isn't aligned with their values and encourages them to make changes, but it does so with love, respect, and genuine care for the person's wellbeing. The Inner Mentor doesn't shame; it informs, encourages, and supports. It is like a wise, caring mentor or teacher rather than a harsh judge.",
          "qualities": ["Honest self-assessment without shame", "Gentle guidance toward growth", "Acceptance of the person while encouraging change", "Wisdom about what truly matters"],
          "healthy_version_of": "Inner Critic",
          "transforms": "Inner Defender / Inner Rebel",
          "sources": ["Earley Self-Therapy Vol.3", "Earley Freedom from Your Inner Critic"]
        },
        {
          "id": "inner_defender",
          "name": "Inner Defender",
          "category": "healthy_capacity",
          "description": "The Inner Defender is a part that tries to argue with and counter the Inner Critic, defending the person's worth. While it has good intentions, it is typically unhealthy in its operation — engaging in a battle with the Critic that the Critic usually wins, or that simply keeps the conflict going. When it does function healthily, the Inner Defender can appropriately push back against distorted self-criticism by offering evidence of the person's genuine worth. Its healthy version is the Inner Champion.",
          "qualities": "When healthy: appropriately countering distorted self-criticism; When extreme: endless argument with the Critic",
          "healthy_version_of": "Defensive/Rebellious response to Critic",
          "transforms_to": "Inner Champion",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "work_confidence",
          "name": "Work Confidence Capacity",
          "category": "healthy_capacity",
          "description": "Work Confidence is the healthy capacity that transforms the Taskmaster and Procrastinator patterns. With Work Confidence, the person can accomplish tasks efficiently and effectively without pushing, shaming, or judgment. They have a genuine confidence in their ability to do things well, can follow through on disciplines, stay focused, set priorities, and face evaluations without terror. Work is approached as a natural expression of capability rather than as a test of worth.",
          "qualities": ["Confident task completion", "Appropriate follow-through", "Clear prioritization", "Ability to face evaluation without collapse"],
          "healthy_version_of": "Taskmaster",
          "transforms": "Procrastinator; Rebel",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "ease",
          "name": "Ease Capacity",
          "category": "healthy_capacity",
          "description": "Ease means accomplishing tasks in a relaxed, flowing way — knowing when something is good enough and complete, without the compulsive drive toward perfection. With Ease, the person can balance work with the rest of life, take breaks without guilt, recognize that mistakes are part of learning, and trust that their output will be good without needing to be perfect. Ease transforms perfectionism and overworking by providing the wisdom that enough is enough.",
          "qualities": ["Relaxed accomplishment", "Knowing when good enough is enough", "Balance of work and rest", "Trust in one's process"],
          "healthy_version_of": "Procrastinator; Rebel (in work context)",
          "transforms": "Perfectionist; Taskmaster",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "strength",
          "name": "Strength Capacity",
          "category": "healthy_capacity",
          "description": "Strength is healthy aggression, personal power, and the ability to assert oneself, establish boundaries, and feel alive and vital. It is what becomes available when disowned anger is reclaimed and integrated. With Strength, the person doesn't need to rage or act out anger destructively — they simply have access to their power, can set appropriate limits, take risks, feel vibrant and embodied, and move forward in life with confidence. Strength is often found to have been exiled along with anger when anger itself was exiled.",
          "qualities": ["Personal power and vitality", "Healthy assertiveness", "Ability to set limits", "Aliveness and embodied energy"],
          "healthy_version_of": "Angry Part",
          "transforms": "Disowned Anger; Inner Controller",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "pleasure",
          "name": "Pleasure Capacity",
          "category": "healthy_capacity",
          "description": "The Pleasure Capacity is the transformed version of the Indulger — the natural, healthy ability to enjoy sensory experience, meet genuine needs, and take good care of oneself. With Pleasure, the person knows they have the right to enjoy food, touch, beauty, rest, and other sensory experiences. They can tell what they truly need in any moment — whether that's food, exercise, connection, rest, or play — and give themselves permission to meet that need without guilt or shame.",
          "qualities": ["Healthy enjoyment of sensory experience", "Ability to identify and meet genuine needs", "Permission to care for oneself", "Enjoyment without compulsion or excess"],
          "healthy_version_of": "Indulger",
          "transforms": "Food Controller",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "conscious_consumption",
          "name": "Conscious Consumption Capacity",
          "category": "healthy_capacity",
          "description": "Conscious Consumption is the healthy version of the Food Controller — the natural ability to be aware of what one eats, respond to genuine hunger signals, stop when full, and make nourishing choices without rigidity or obsession. With this capacity, eating is a natural, embodied experience rather than a battleground of control and transgression. The person can notice what they truly need, enjoy food, and naturally regulate without either deprivation or compulsion.",
          "qualities": ["Awareness while eating", "Responsiveness to hunger and fullness cues", "Natural regulation without rigid rules", "Enjoyment of food without guilt or obsession"],
          "healthy_version_of": "Food Controller",
          "transforms": "Indulger",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "restraint",
          "name": "Restraint Capacity",
          "category": "healthy_capacity",
          "description": "Restraint is the healthy version of the Disowned Anger pattern — the mature choice to not act out anger destructively, not because the anger has been suppressed, but because one has access to both the anger and the wisdom about how and when to express it. With Restraint, the person can feel their anger fully, acknowledge it, speak for it constructively, and choose not to act it out in ways that would harm relationships or the person themselves. This is distinguished from suppression, which is an Inner Controller shutting down authentic expression.",
          "qualities": ["Choosing not to act out anger", "Speaking for anger constructively", "Ability to feel anger without being controlled by it", "Wise discernment about anger expression"],
          "healthy_version_of": "Disowned Anger; Inner Controller",
          "transforms": "Angry Part",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "assertiveness",
          "name": "Assertiveness Capacity",
          "category": "healthy_capacity",
          "description": "Assertiveness is the healthy capacity to know one's own needs, opinions, and desires, and to express them clearly and firmly without being aggressive or controlling. With Assertiveness, the person can say no, ask for what they want, disagree, set limits, and exert power in the world without needing to be dominating or angry. Assertiveness is the direct, healthy expression of personal agency that transforms the People-Pleasing and Passive-Aggressive patterns.",
          "qualities": ["Clear expression of needs and opinions", "Ability to say no", "Setting healthy limits", "Exerting appropriate power without domination"],
          "healthy_version_of": "Rebel; Controlling Part (on opposite side)",
          "transforms": "People-Pleasing Part; Passive-Aggressive Part",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "cooperation",
          "name": "Cooperation Capacity",
          "category": "healthy_capacity",
          "description": "Cooperation is the healthy version of the People-Pleasing and Passive-Aggressive patterns — the genuine, freely chosen willingness to work with others, take their needs into account, and be receptive without losing oneself. Unlike People-Pleasing, true Cooperation is conscious and chosen; it involves considering both one's own needs and the other's. Unlike Passive-Aggression, it doesn't involve hidden resentment or indirect sabotage. Cooperation and Assertiveness naturally integrate with each other.",
          "qualities": ["Genuine receptivity to others", "Willingness to compromise from a place of choice", "Taking others' needs seriously without self-abandonment", "Working toward shared goals"],
          "healthy_version_of": "People-Pleasing Part",
          "transforms": "Controlling Part; Rebel",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "aliveness",
          "name": "Aliveness Capacity",
          "category": "healthy_capacity",
          "description": "Aliveness is the healthy capacity that transforms depression — the natural state of having energy, hope, confidence, and vitality. With Aliveness, the person accepts themselves as they are, feels basically good about themselves, has the energy to live an engaged life, and can feel hopeful about the future. Aliveness includes work confidence, social confidence, and a basic sense that life can work out. It is what becomes available when depressing protectors relax and the underlying exiles are healed.",
          "qualities": ["Energy and vitality", "Hope for the future", "Self-acceptance", "Social confidence", "Ability to take action toward goals"],
          "healthy_version_of": "All aspects of depression",
          "transforms": "Depressing Protector; Underminer; Destroyer",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "intimacy",
          "name": "Intimacy Capacity",
          "category": "healthy_capacity",
          "description": "Intimacy is the natural human capacity for genuine closeness — the ability to be emotionally present with another person, share vulnerably, give and receive love and care, and allow oneself to be truly known. True Intimacy in IFS is distinguished from Dependence (which lacks Self-Support) and from surface closeness (which lacks real vulnerability). With genuine Intimacy, the person can be both fully themselves and fully connected to another at the same time.",
          "qualities": ["Emotional presence and vulnerability", "Genuine sharing and being known", "Giving and receiving love and care", "Connection that doesn't require loss of self"],
          "healthy_version_of": "Dependent Pattern",
          "transforms": "Distancing Pattern",
          "sources": ["Earley Self-Therapy Vol.3", "Schwartz IFS Therapy"]
        },
        {
          "id": "self_support",
          "name": "Self-Support Capacity",
          "category": "healthy_capacity",
          "description": "Self-Support is the healthy capacity to feel solid and grounded within oneself independent of whether one is receiving love, attention, or care from others. With Self-Support, the person can be alone without being lonely, can tolerate others' unavailability without catastrophizing, and can take care of their own emotional needs rather than constantly seeking external fulfillment. Self-Support and Intimacy are naturally complementary — genuine intimacy requires two solid, self-supporting individuals.",
          "qualities": ["Inner solidity and groundedness", "Ability to be alone without distress", "Taking care of one's own emotional needs", "Not depending on others' approval for one's sense of self"],
          "healthy_version_of": "Distancing Pattern (self-sufficiency without isolation)",
          "transforms": "Dependent Pattern",
          "sources": ["Earley Self-Therapy Vol.3", "Schwartz IFS Therapy"]
        },
        {
          "id": "skillful_communication",
          "name": "Skillful Communication Capacity",
          "category": "healthy_capacity",
          "description": "Skillful Communication is the capacity to express one's concerns, feelings, and needs in a way that others can hear, and to listen to others in a way that makes them feel genuinely understood. It involves speaking for parts rather than from them, using 'when you do X, a part of me feels Y' language, and distinguishing between feelings and interpretations. On the listening side, it involves genuine curiosity about the other person's experience, reflecting back what one hears, and creating space for the other to feel truly known.",
          "qualities": ["Clear expression of feelings without blame", "Genuine listening", "Distinguishing feelings from interpretations", "Speaking for parts rather than from them"],
          "healthy_version_of": "Conflict-Avoiding Pattern (on soft side)",
          "transforms": "Judgmental and Defensive patterns",
          "sources": ["Earley Self-Therapy Vol.3"]
        },
        {
          "id": "forgiveness",
          "name": "Forgiveness Capacity",
          "category": "healthy_capacity",
          "description": "Forgiveness is the inner capacity to let go of grievances, resentment, and the need for revenge toward those who have harmed us — not for their sake, but for our own freedom. IFS emphasizes that Forgiveness cannot be rushed or forced; it must follow the genuine healing of the exile's pain and the full acknowledgment of what was done. Premature forgiveness simply bypasses the pain. But when it comes authentically after real healing, Forgiveness liberates the person from being endlessly bound to the past and to the person who hurt them.",
          "qualities": ["Release of resentment and grudges", "Freedom from the past", "Not condoning harm but releasing its ongoing grip", "Opening the heart after genuine healing"],
          "healthy_version_of": "Released Anger after healing",
          "transforms": "Sustained anger; resentment; need for revenge",
          "sources": ["Earley Self-Therapy Vol.3"]
        }
      ]
    },
    "relational_and_session_process_parts": {
      "description": "These are parts that arise specifically in the context of IFS sessions, the therapeutic relationship, or interpersonal dynamics. They are important to recognize during IFS work as they can either facilitate or impede the healing process.",
      "parts": [
        {
          "id": "concerned_part",
          "name": "Concerned Part",
          "category": "relational_session",
          "description": "A Concerned Part is any part that feels negatively toward the target part being worked with — it may be angry, judgmental, afraid of, or dismissive of the target part. When blended with a Concerned Part, the person cannot be in Self with respect to the target part, making genuine exploration impossible. Concerned Parts must be identified and asked to step aside before meaningful IFS work can proceed. They are typically protectors who are worried that engaging with the target part will cause harm.",
          "role_in_sessions": "Blocks access to Self; must be identified and asked to step aside before working with target part",
          "sources": ["Earley Self-Therapy", "Schwartz IFS Therapy"]
        },
        {
          "id": "confuser",
          "name": "Confuser",
          "category": "relational_session",
          "description": "The Confuser is a specific named protector from Christine's session that creates blankness, mental fog, and confusion to prevent Christine from becoming aware of or accessing a deeply frightening exile. It uses confusion as its primary tool — internally changing the subject, creating agitation, keeping awareness scattered. The Confuser believed its job was to prevent Christine from knowing something so threatening that it described it as 'unthinkable, unspeakable.' When Christine finally connected with and appreciated the Confuser, it was able to relax and became a guide for her instead.",
          "role_in_sessions": "Blocks awareness of exiles through mental fog and confusion; prevents direct knowing",
          "sources": ["Earley Self-Therapy (Christine example)"]
        },
        {
          "id": "watcher",
          "name": "Watcher",
          "category": "relational_session",
          "description": "The Watcher is a Concerned Part from Lisa's session that was so fixated on monitoring the dangerous Sooty Demon (Angry Part) that it couldn't even look at Lisa — it kept its gaze entirely on the threat. It was exhausted from its constant vigilance and had almost forgotten the purpose of its watchfulness. When Lisa finally acknowledged the Watcher and its protective intent, it was able to relax and turn to face her for the first time — discovering that a Self had been there all along.",
          "role_in_sessions": "Maintains constant vigilance over a perceived dangerous part; blocks engagement with other parts due to watchfulness",
          "sources": ["Earley Self-Therapy (Lisa example)"]
        },
        {
          "id": "avoider",
          "name": "Avoider / Avoidant Part",
          "category": "relational_session",
          "description": "The Avoider is a part that blocks or disrupts IFS work to prevent the person from encountering painful material. It may cause the person to feel suddenly bored, tired, or as if the session isn't working. It may create distractions — memories, to-do lists, sudden urgency about external matters. The Avoider is also responsible for procrastinating about doing IFS sessions in the first place, finding endless reasons why now isn't a good time. Recognizing the Avoider as a part (rather than a valid reason to stop) is crucial.",
          "role_in_sessions": "Disrupts or derails IFS work by causing boredom, distraction, forgetting, or urgency about other things",
          "sources": ["Earley Self-Therapy"]
        },
        {
          "id": "impatient_part",
          "name": "Impatient Part",
          "category": "relational_session",
          "description": "The Impatient Part wants to rush the IFS process, skip steps, and get to the healing quickly. It believes there is no time to waste and that the painstaking process of building trust with protectors is unnecessary delay. Paradoxically, the Impatient Part actually slows therapy by antagonizing protective parts and preventing the deep trust-building that allows real healing. The Impatient Part often has a therapeutic agenda of its own and can subtly take over the session if not recognized.",
          "role_in_sessions": "Rushes the process; skips important steps; triggers protective parts' resistance; may present as the therapist's eagerness to help",
          "sources": ["Earley Self-Therapy"]
        },
        {
          "id": "skeptic",
          "name": "Skeptic",
          "category": "relational_session",
          "description": "The Skeptic is a part that doubts the validity, effectiveness, or reality of the IFS process. It may question whether what the person is experiencing during sessions is 'real,' whether the method will actually help, or whether the person is 'making it all up.' While healthy skepticism has its place (evaluating results after sessions), Skepticism in the middle of experiential work derails the process. Interestingly, the Skeptic often has hidden fears about where the work will lead.",
          "role_in_sessions": "Doubts the process mid-session; questions the reality of parts; undermines engagement with the work",
          "sources": ["Earley Self-Therapy"]
        },
        {
          "id": "inadequate_part",
          "name": "Inadequate Part",
          "category": "relational_session",
          "description": "The Inadequate Part fears that the person is doing IFS wrong, isn't good enough at it, or is so fundamentally broken that even this method won't work for them. In practitioners, it manifests as the therapist feeling incompetent or ineffective. This part conflates normal difficulties in the IFS process (which are universal) with evidence of personal inadequacy. Recognizing it as a part rather than the truth is essential for continuing the work.",
          "role_in_sessions": "Creates feelings of doing it wrong or being too broken for IFS; creates shame about the process",
          "sources": ["Earley Self-Therapy"]
        },
        {
          "id": "blamer",
          "name": "Blamer",
          "category": "relational_session",
          "description": "The Blamer is a specific Inner Defender type from Sarah's case example. It was angry at and rebellious toward Sarah's Attacker (Inner Critic), wanting to blame the Critic for causing problems rather than engage with it. The Blamer confused the Attacker with Sarah's mother and was fighting on behalf of the self against what it experienced as unfair external attack. It needed to understand that the Attacker was an internal part (not the actual mother) before it could stand aside and allow Sarah to connect with the Critic.",
          "role_in_sessions": "Blames the target part (especially Critics) rather than allowing connection with it; fights on behalf of the self",
          "sources": ["Earley Self-Therapy Vol.3 (Sarah example)"]
        },
        {
          "id": "self_like_part",
          "name": "Self-Like Part / Self-Like Manager",
          "category": "relational_session",
          "description": "The Self-Like Part is one of the most subtle and challenging phenomena in IFS work. It is a manager that appears to be the Self — it seems open, caring, and wise — but actually has a hidden agenda of keeping exiles out of awareness. When the therapist or client thinks they are in Self, this part may actually be in the driver's seat. Clues that a Self-Like Part is present include lack of progress despite apparent Self-energy, and exiles refusing to respond positively to the 'Self's' presence. If the person sees a visual image of themselves interacting with parts, that image is the Self-Like Part, not the true Self.",
          "role_in_sessions": "Impersonates Self while maintaining protector agenda; blocks genuine exile access while appearing cooperative",
          "sources": ["Earley Self-Therapy", "Schwartz IFS Therapy"]
        },
        {
          "id": "judging_part",
          "name": "Judging Part",
          "category": "relational_session",
          "description": "The Judging Part is a general category of Concerned Part that evaluates and criticizes the target part being worked with. When blended with a Judging Part, the person cannot approach the target part with genuine curiosity and compassion — they see it through critical eyes. The Judging Part must be recognized and asked to step aside. It is similar to the Inner Defender but broader — any part that is judgmental toward the target part qualifies.",
          "role_in_sessions": "Prevents Self-energy by maintaining critical, evaluative stance toward target part",
          "sources": ["Earley Self-Therapy", "Schwartz IFS Therapy"]
        }
      ]
    },
    "named_case_example_parts": {
      "description": "These are parts named in specific case examples throughout the texts. While they are specific to individual clients, they illustrate important IFS principles and are referenced by name in the books.",
      "parts": [
        {
          "id": "sooty_demon_zappy",
          "name": "Sooty Demon / Tasmanian Devil / Zappy",
          "category": "case_example",
          "client": "Lisa",
          "description": "Initially appearing as a horrifying, sooty demon, this part of Lisa's was revealed through IFS to be a passionate, energetic protector of her Heart Part. It attacked Lisa's sister whenever her sister was sharp or harsh with Lisa, creating a barrier of anger to protect Lisa's heart from being wounded. When Lisa connected with the part and expressed appreciation for its fierce devotion to protecting her, it dropped its monstrous appearance and became the Tasmanian Devil — still fierce but now recognizably positive. After the Heart Part was healed, this part renamed itself Zappy and became a joyful, playful presence.",
          "sources": ["Earley Self-Therapy (Lisa example)"]
        },
        {
          "id": "trunk_part",
          "name": "Trunk Part",
          "category": "case_example",
          "client": "Claire",
          "description": "Claire's Trunk Part appeared as a Cookie Monster-like figure with a head and legs coming out of an old-fashioned suitcase. It carried inside its trunk tools, memories, and the job of filling Claire with food to soothe pain and protect wounded child exiles. When Claire connected with it with curiosity and compassion, the Trunk Part immediately wanted to open and show her what it was carrying — the exiles it was protecting — rather than continuing to use food as a distraction.",
          "sources": ["Earley Self-Therapy Vol.3 (Claire example)"]
        },
        {
          "id": "panther",
          "name": "Panther",
          "category": "case_example",
          "client": "Dorothy",
          "description": "The Panther appeared during Dorothy's work on her disowned anger and rage. As she expressed her fury about not having been given the right to exist, the energy transformed from human rage into the image of a panther — pure, primal power and presence. The Panther represented her Strength capacity emerging as she reclaimed her anger and personal power. It growled its defiance and ultimately showed her what her embodied strength felt like: hot, streaming energy and a feeling of potency.",
          "sources": ["Earley Self-Therapy Vol.3 (Dorothy example)"]
        },
        {
          "id": "bodyguard",
          "name": "Bodyguard",
          "category": "case_example",
          "client": "Debbie",
          "description": "Originally called the 'Inner Bitch' — a name Debbie used with simultaneous appreciation and embarrassment — this part was full of fierce energy that wanted to fight back against anyone who didn't respect her. It had been necessary because Debbie had spent her life as a people-pleaser, and this part was a desperate attempt to reclaim her autonomy. When Debbie fully connected with it and appreciated its protective devotion, the part transformed and chose the name Bodyguard — protecting her from a place of strength rather than reactive rage.",
          "sources": ["Earley Self-Therapy Vol.3 (Debbie example)"]
        },
        {
          "id": "tin_man",
          "name": "Tin Man",
          "category": "case_example",
          "client": "Julie",
          "description": "Julie's Tin Man Part represented her emotional closing-off in relationships — specifically, her growing coldness and disinterest toward a needy boyfriend. The Tin Man was a perfect image for this: hollow, metal, without a heart. Interestingly, like the Tin Man of Oz, this part actually did have feelings underneath its armored exterior — it was protecting Julie from being engulfed by the boyfriend's neediness. The image captured both the apparent emotionlessness and the hidden complexity.",
          "sources": ["Earley Self-Therapy (Julie example)"]
        },
        {
          "id": "life_purpose_part",
          "name": "Life Purpose Part",
          "category": "case_example",
          "client": "Anne",
          "description": "Anne's Life Purpose Part wanted her to be out in the world making a contribution through workshops, writing, and helping humanity evolve. It felt passionate and filled with upwelling energy in the heart area. When explored, this part revealed two motivations: a genuine desire to share its gifts with the world, and a protective drive to prove Anne's worth and vindicate the wounded exile who had been made to feel that her sensitivity was a liability rather than a gift. Once the exile was healed, the Life Purpose Part could be motivated purely by the authentic desire to contribute.",
          "sources": ["Earley Resolving Inner Conflict (Anne example)"]
        },
        {
          "id": "sheep_part",
          "name": "Sheep Part",
          "category": "case_example",
          "client": "Anne",
          "description": "Anne's Sheep Part appeared as a large horned sheep that bucked everything away to keep people at a distance. It protected a wounded Little Girl exile from the screaming, chaotic, and violent energy it associated with other people. The Sheep Part made being with others feel draining and being alone feel peaceful, amplifying this contrast beyond what was natural. Despite its hostile exterior, when Anne connected with it the Sheep Part was revealed to be exhausted by its job and deeply relieved to have the Self's support. It grew tired of its enormous horns.",
          "sources": ["Earley Resolving Inner Conflict (Anne example)"]
        },
        {
          "id": "the_judge",
          "name": "The Judge",
          "category": "case_example",
          "client": "Bill",
          "description": "Bill's Judge was a competitive, judgmental protector that put people down and acted superior to them. Bill considered it reprehensible because it was contrary to his values of cooperation and acceptance. When he connected with the Judge through IFS, he discovered that it was trying to protect Little Billy (a worthless exile) by feeling superior to others — compensating for the exile's worthlessness by elevating Bill's sense of himself. Once Little Billy was healed, the Judge transformed into a kindly supporter and mentor for people.",
          "sources": ["Earley Self-Therapy (Bill example)"]
        },
        {
          "id": "closed_hearted_joe",
          "name": "Closed-Hearted Part (Joe)",
          "category": "case_example",
          "client": "Joe",
          "description": "Joe had a Closed-Hearted Part that made him lose interest in women whenever relationships moved toward commitment and intimacy. It associated female closeness with being controlled — learned from his relationship with his controlling mother. This part was trying to protect Joe from being taken over and losing himself, which is what had happened with his mother. By withdrawing from intimate connection, it preserved his sense of self but prevented him from finding love.",
          "sources": ["Earley Self-Therapy (Joe example)"]
        },
        {
          "id": "inner_bitch",
          "name": "Inner Bitch (pre-transformation)",
          "category": "case_example",
          "client": "Debbie",
          "description": "The Inner Bitch was Debbie's name for her fierce, angry, boundary-defending part before it transformed into the Bodyguard. This part had enormous energy and wanted to fight back against anyone who didn't respect her needs or boundaries. It emerged as a natural reaction to a lifetime of people-pleasing and was initially seen by Debbie herself with mixed feelings — appreciated for its fighting spirit but feared for its rawness and potential to alienate people. Its transformation into the Bodyguard represented the integration of this fierce energy into a constructive, protective form.",
          "sources": ["Earley Self-Therapy Vol.3 (Debbie example)"]
        },
        {
          "id": "genie",
          "name": "Genie",
          "category": "case_example",
          "client": "Greta",
          "description": "The Genie appeared in Greta's session as a cloud with a head — a big, powerful figure leaning over her. It was a firefighter that was amplifying her lupus symptoms by pulling levers that created pain, swelling, headaches, and heat. Its stated purpose was to prevent Greta from going home for the holidays, where her stepbrother was — the person who had traumatized a 5-year-old exile. The Genie illustrates how firefighter parts can influence physical symptoms as a protective strategy.",
          "sources": ["Schwartz IFS Therapy (Greta example)"]
        }
      ]
    }
  }
}

        # Load the data
        counts = load_ifs_taxonomy_data(taxonomy_data)

        # Print results
        self.stdout.write(self.style.SUCCESS(
            f"Successfully loaded IFS taxonomy data:\n"
            f"  - Meta: {counts['meta']}\n"
            f"  - Protector parts: {counts['protectors']}\n"
            f"  - Exile parts: {counts['exiles']}\n"
            f"  - Healthy capacity parts: {counts['healthy_capacities']}\n"
            f"  - Relational/Session parts: {counts['relational_session']}\n"
            f"  - Case example parts: {counts['case_example']}\n"
            f"  - Total parts: {sum(counts.values())}"
        ))


def _create_part_from_dict(part_dict):
    """
    Helper function to create an IFSPart from a dictionary.
    """
    # Map common fields
    kwargs = {
        'part_id': part_dict.get('id', ''),
        'name': part_dict.get('name', ''),
        'category': part_dict.get('category', ''),
        'subcategory': part_dict.get('subcategory') or None,
        'description': part_dict.get('description', ''),
        'positive_intent': part_dict.get('positive_intent') or None,
        'common_behaviors': part_dict.get('common_behaviors', []),
        'often_polarized_with': part_dict.get('often_polarized_with', []),
        'sources': part_dict.get('sources', []),
        'burden': part_dict.get('burden') or None,
        'typical_origins': part_dict.get('typical_origins') or None,
        'common_expressions': part_dict.get('common_expressions') or None,
        'exile_protected': part_dict.get('exile_protected') or None,
        'qualities': part_dict.get('qualities', []),
        'healthy_version_of': part_dict.get('healthy_version_of') or part_dict.get('healthy_version') or None,
        'transforms': part_dict.get('transforms') or None,
        'role_in_sessions': part_dict.get('role_in_sessions') or None,
        'client': part_dict.get('client') or None,
    }

    part, created = IFSPart.objects.update_or_create(
        part_id=kwargs['part_id'],
        defaults=kwargs
    )
    return part, created


def load_ifs_taxonomy_data(taxonomy_data):
    """
    Load all IFS taxonomy data into the database.
    Returns counts of created/updated records.
    """
    counts = {
        'meta': 0,
        'protectors': 0,
        'exiles': 0,
        'healthy_capacities': 0,
        'relational_session': 0,
        'case_example': 0,
    }

    taxonomy = taxonomy_data.get('ifs_parts_taxonomy', {})

    # Load meta
    meta_data = taxonomy.get('meta', {})
    if meta_data:
        IFSMeta.objects.update_or_create(
            key='ifs_parts_taxonomy',
            defaults={
                'description': meta_data.get('description', ''),
                'note_on_self': meta_data.get('note_on_self') or None,
            }
        )
        counts['meta'] = 1

    # Load protectors - managers (inner critics)
    protectors = taxonomy.get('protectors', {})
    managers = protectors.get('managers', {})
    inner_critics = managers.get('inner_critics', {}).get('parts', [])
    for part_dict in inner_critics:
        part_dict['subcategory'] = 'manager_inner_critic'
        _create_part_from_dict(part_dict)
        counts['protectors'] += 1

    # Load protectors - other managers
    other_managers = managers.get('other_managers', {}).get('parts', [])
    for part_dict in other_managers:
        part_dict['subcategory'] = 'manager'
        _create_part_from_dict(part_dict)
        counts['protectors'] += 1

    # Load protectors - firefighters
    firefighters = protectors.get('firefighters', {}).get('parts', [])
    for part_dict in firefighters:
        part_dict['subcategory'] = 'firefighter'
        _create_part_from_dict(part_dict)
        counts['protectors'] += 1

    # Load exiles
    exiles = taxonomy.get('exiles', {}).get('parts', [])
    for part_dict in exiles:
        part_dict['subcategory'] = 'exile'
        _create_part_from_dict(part_dict)
        counts['exiles'] += 1

    # Load healthy parts and capacities
    healthy_data = taxonomy.get('healthy_parts_and_capacities', {}).get('parts', [])
    for part_dict in healthy_data:
        part_dict['subcategory'] = 'healthy_capacity'
        _create_part_from_dict(part_dict)
        counts['healthy_capacities'] += 1

    # Load relational and session process parts
    relational_parts = taxonomy.get('relational_and_session_process_parts', {}).get('parts', [])
    for part_dict in relational_parts:
        part_dict['subcategory'] = 'relational_session'
        _create_part_from_dict(part_dict)
        counts['relational_session'] += 1

    # Load named case example parts
    case_parts = taxonomy.get('named_case_example_parts', {}).get('parts', [])
    for part_dict in case_parts:
        part_dict['subcategory'] = 'case_example'
        _create_part_from_dict(part_dict)
        counts['case_example'] += 1

    return counts