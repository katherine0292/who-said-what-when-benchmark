"""Draft QA edits based on the two submitted annotation rounds.

Each row: QA number, question without answer, key-point references, selected turns
(or None for the submitted IDs), reason for any editorial evidence change.
These are text-based editorial judgments; the pilot still requires listening.
"""
EDITS = {
    1: ("Who argued that sharing food can help people overcome fear of one another, and how? When was this said?",
        ["Sharing a meal makes common ground visible.", "A shared experience can reduce fear and hostility."], None, None),
    2: ("Who described the American diner as an unusually inclusive place, and why? When was this said?",
        ["People of very different means sit at the same counter.", "They receive the same welcome and service."], None, None),
    3: ("Who recounted an unexpected Juilliard audition as a child, and how did it come about? When was this said?",
        ["Her mother encouraged her to walk in without an invitation.", "She auditioned on the spot about 30 minutes later."], [4, 6], "The actual audition and age confirmation occur in turn 6; turn 4 supplies the setup."),
    4: ("Who recommended a self-affirmation exercise after a loss of identity, and what does it involve? When was this said?",
        ["Write down qualities that do not depend on external roles or circumstances.", "Use these enduring qualities as an anchor during change."], None, None),
    5: ("Who explained identity foreclosure, and why can it become a problem after a life change? When was this said?",
        ["It means committing early to one identity without exploring alternatives.", "Losing that role can leave the person without a stable sense of self."], None, None),
    6: ("Who explained why uncertainty can lead to a mental spiral, and what was the explanation? When was this said?",
        ["Major change can make a person feel uncertain and out of control.", "Overthinking creates a misleading sense of control over an unclear situation."], None, None),
    7: ("Who defined cognitive reappraisal, and what changes when a person uses it? When was this said?",
        ["Interpret the same situation in a different way.", "The new interpretation changes its emotional impact."], None, None),
    8: ("Who asked about an extra pressure teenagers face while developing an identity, and what was the pressure? When was this said?",
        ["Teenagers face pressure to curate a personal brand from an unusually early age."], None, None),
    9: ("Who described a study on adolescent self-esteem, and what did participants do and what happened? When was this said?",
        ["Ninth graders spent about five minutes writing about identities that mattered to them.", "The exercise group maintained self-esteem through the transition instead of showing the usual decline."], None, None),
    10: ("Who asked whether reaffirming identities can have a downside for peer groups, and what was the concern? When was this said?",
         ["It could encourage othering.", "Peers might be bullied or made to feel outside the group."], None, None),
    11: ("Who raised a concern about representation in television and what possible downside did they identify? When was this said?",
         ["Increased representation can be valuable.", "Some portrayals might also reinforce stereotypes."], None, None),
    12: ("Who asked about the role adults play in how adolescents see themselves, and what risk did they raise? When was this said?",
         ["Adults and experts may tell adolescents who they are.", "The speaker questions whether imposing those definitions can be harmful."], None, None),
    13: ("Who introduced a three-stage model of influence, and what role does the first stage play? When was this said?",
         ["The PCP model begins with perception.", "Changing how someone frames the situation is the proposed first step in changing the decision."], None, None),
    14: ("Who explained how exposing a social script changes perception and what comes next in the model? Give the two supporting segments.",
         ["Calling attention to an implicit script can weaken its effect and reframe the interaction.", "After shifting perception, the proposed next step is to change context."], [1, 7], "Per-clip Round 2 supports two non-contiguous turns; the aggregate lists only one."),
    15: ("Who described negative dissociation, and how is it supposed to work? When was this said?",
         ["Mention a group or behavior the listener does not identify with, such as closed-mindedness.", "The speaker proposes that distancing from that trait makes the listener act more open-minded."], None, None),
    16: ("Who described a shortcut for influencing others, and what was the suggestion? When was this said?",
         ["Identify an unmet need or insecurity.", "The speaker proposes meeting that need as a way to influence behavior."], None, None),
    17: ("Who explained why people keep using an ineffective strategy, and what alternative did they propose? When was this said?",
         ["Attachment to being right keeps people using ineffective methods.", "Try uncomfortable approaches and accept being wrong while learning what works."], None, None),
    18: ("Who distinguished a situation from a problem, and what should one do about each? Give the supporting segments.",
         ["A situation cannot be changed and has to be accepted.", "A problem has a solution even if taking it is uncomfortable."], [2, 4], "Round 2 combines turns 2 and 4; intervening turn 3 is a different speaker."),
    19: ("Who urged people to choose themselves rather than wait to be chosen, and what would that involve? When was this said?",
         ["Stop waiting for gatekeepers to grant permission.", "Take responsibility for leading or sharing your work despite the risk of failure."], None, None),
    20: ("Who discussed waiting for outside approval, and what did they say it accomplishes and suggest doing instead? When was this said?",
         ["Waiting for approval can protect people from the risk of failure.", "Keep the larger goal and start sharing work now, for example through a blog or an online recording."], [2, 3], "The explanation is in turn 2 and the specific alternative is in adjacent turn 3."),
    21: ("Who proposed a small first step to overcome long-term hesitation, and what example was given? When was this said?",
         ["Start with the smallest viable effort or audience.", "An example is spending a couple of hours a week volunteering."], None, None),
    22: ("Who urged people to start before they could do something perfectly, and what examples were given? When was this said?",
         ["Begin with imperfect attempts instead of waiting to get everything right.", "Examples include writing a bad blog post or delivering an imperfect speech."], None, None),
    23: ("Who explained internal resistance and suggested how to act despite it? When was this said?",
         ["Resistance persists because it seeks to keep people safe.", "Take a small action while fear is still present instead of waiting for it to disappear."], None, None),
    24: ("Who questioned whether authenticity is useful in professional work, what did they propose instead, and how did they suggest practicing it? Give the supporting segments.",
         ["The speaker dismisses authenticity as a professional ideal.", "Consistency is more useful when serving an audience.", "Practice acting as the best version of yourself."], [2, 4, 8], "The original target only covers the critique. Replacement and practice occur in turns 4 and 8; the full clip version of the turn labels exceeds the local audio duration."),
    25: ("Who explained the components of authority, and what effect did they claim that physical composure has? When was this said?",
         ["Authority involves perceived right to lead and perceived survival or social value.", "The speaker claims stillness or composure can make others perceive authority."], None, None),
}

# Perceived delivery labels; these are not psychological states or gold emotion labels.
TONE = {
    1: "animated", 2: "warm", 3: "animated", 4: "encouraging", 5: "explanatory",
    6: "reflective", 7: "explanatory", 8: "concerned", 9: "emphatic", 10: "inquiring",
    11: "inquiring", 12: "inquiring", 13: "explanatory", 14: "explanatory",
    15: "explanatory", 16: "explanatory", 17: "reflective", 18: "explanatory",
    19: "reflective", 20: "reflective", 21: "encouraging", 22: "encouraging",
    23: "emphatic", 24: "emphatic", 25: "explanatory",
}

# Origin and evidence problems requiring media review, not automatic repair.
REVIEW = {
    "v1-1": ["origin_duration_mismatch"],
    "v1-2": ["origin_duration_mismatch"],
    "v3-2": ["duplicate_source_window"],
    "v3-3": ["duplicate_source_window", "origin_duration_mismatch", "legacy_turn_clock_errors"],
    "v4-3": ["turns_exceed_local_audio"],
    "v5-1": ["origin_duration_mismatch"],
    "v5-8": ["turns_exceed_local_audio", "aggregate_round2_conflict"],
}
