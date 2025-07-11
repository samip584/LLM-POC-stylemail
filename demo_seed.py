#!/usr/bin/env python3
"""
Demo Data Seeding Script for StyleMail POC

This script populates the StyleMail system with sample users and their writing styles
to demonstrate the AI's ability to learn and mimic different communication styles.
"""

import requests
import sys
from typing import List, Dict

API_BASE_URL = "http://localhost:8000"

# Sample writing styles for different personas
DEMO_USERS = [
    {
        "user_id": "pirate_pete",
        "description": "Pirate-speak with nautical terms",
        "samples": [
            "Ahoy matey! Aye, I've received yer message and will be chartin' a course to address this matter post-haste! The crew and I have been sailin' through rough waters lately, but we're committed to delivering the finest results ye ever did see. Rest assured, we'll be navigatin' these challenges with the skill and determination that only seasoned sailors possess!",
            "Arrr! That be a fine idea indeed! Let's hoist the sails and set forth on this venture, savvy? I've been ponderin' over the details all night whilst standin' watch on the quarterdeck, and I must say, this plan has more promise than a chest full of Spanish doubloons! We'll need all hands on deck to make this work, but with our combined efforts and a fair wind at our backs, we'll conquer these seas of opportunity!",
            "Avast! I be thankin' ye for yer hard work on this project, ye scurvy dog! Yer efforts be worth their weight in doubloons, they are! I've sailed the seven seas for many a year, and rarely have I witnessed such dedication and craftsmanship. The cap'n himself would be mighty impressed with what ye've accomplished here. Keep up this stellar work, and there'll be extra grog rations for all!",
            "Shiver me timbers! That deadline be approachin' like a storm on the horizon, faster than a British man-o'-war in full pursuit! All hands on deck, mates! We need every soul workin' together if we're gonna weather this tempest and bring our ship safely to port. I've been studyin' the charts and preparin' our course of action, so gather 'round and let's set our strategy before the wind picks up!",
            "Yo ho ho! I'll be reviewin' these documents whilst sailin' the seven seas of data, navigatin' through every detail with the precision of a master cartographer! Expect me report by sundown, or I'll walk the plank myself! I've assembled me best crew members to help analyze every piece of information, and we'll be deliverin' insights sharper than a cutlass and more valuable than the treasure of the Caribbean!"
        ]
    },
    {
        "user_id": "priya_sharma",
        "description": "Warm Nepali professional with cultural references",
        "samples": [
            "Namaste ji! I hope this message finds you and your family in good health and high spirits. I wanted to reach out regarding our upcoming project deadline, and I must say, your dedication reminds me of the perseverance we show during Dashain preparations! I've been reviewing all the materials you sent, and I'm thoroughly impressed with the attention to detail. Let me know when you have time for a quick chai and discussion about the next steps, okay?",
            "Hello there! Thank you so much for your patience with this matter - your understanding means the world to me, truly! You know, working with you feels like the warmth of sitting around a fire during the cold Kathmandu winter. I've been coordinating with the team here, and everyone is so excited about moving forward with your suggestions. Please don't hesitate to call me anytime - my door is always open, just like we keep our homes open for guests during festivals!",
            "Dear colleague, I hope you're doing well! I wanted to follow up on our conversation from last week about the project timeline. You know, this reminds me of climbing the hills back home - sometimes the journey takes longer than expected, but the view from the top is always worth it! I've been working day and night to ensure everything is perfect, and I'm confident we'll achieve something truly beautiful together. Looking forward to hearing your thoughts!",
            "Greetings! I trust this email finds you in the best of health and happiness. I wanted to share some updates about our initiative, and I must tell you, the progress we've made fills my heart with the same joy as seeing the mountains on a clear morning! The entire team has been working with such passion and commitment - it's like organizing a proper bhoj where everyone contributes their special dish! Please let me know if you need any clarification or support from my end.",
            "Hello my friend! I hope you and yours are doing wonderfully well. I was just thinking about our project while having my morning chiya, and I realized we should definitely schedule a meeting to discuss the finer details. Your insights are always so valuable, just like the wisdom our elders share during family gatherings! I've prepared a comprehensive overview of everything we've accomplished so far, and I'm eager to get your feedback. Shall we connect sometime this week?"
        ]
    },
    {
        "user_id": "valley_girl_vanessa",
        "description": "Valley girl speak with 'like' and 'literally'",
        "samples": [
            "OMG, like, this is literally the best proposal I've ever seen in my entire life! Like, seriously, you totally crushed it beyond belief! 💅 I was, like, sitting here reading through everything and I literally couldn't believe how amazing it all is! Like, the attention to detail? Absolutely incredible! And the way you structured everything? Like, it's literally perfect! I'm so, so, so excited to move forward with this, and I just know it's gonna be, like, totally amazing!",
            "So, like, I was literally just thinking about this exact thing this morning and, like, we should totally meet up and discuss it in person? Like, for real though! I feel like this is, like, one of those opportunities that comes along once in a blue moon, you know? And I'm literally so stoked about the possibilities! Like, we could totally make this into something huge! I'm thinking we should, like, grab coffee or lunch sometime this week and really dive deep into all the details!",
            "This is, like, literally so important right now that I can't even express it properly! Like, we need to, like, prioritize this ASAP because it's, like, super duper critical to everything we're trying to accomplish! I've been, like, thinking about this nonstop - literally couldn't sleep last night because my brain was just going crazy with ideas! Like, the potential here is absolutely insane! We should totally get the whole team together and brainstorm because, like, everyone needs to be part of this journey!",
            "I'm literally so excited about this project that I can barely contain myself! Like, it's going to be, like, absolutely amazing and transformative! I can't even deal with how good this is gonna be when we're done! Like, seriously though, the impact this could have is, like, mind-blowing! I've been telling everyone about it - like literally everyone I know - because I'm just that passionate about making this work! This is gonna be, like, our biggest achievement yet!",
            "So basically, like, what I'm saying is, like, we should literally just go for it with full force and commitment, you know? Like, why not, right? Life's too short to not pursue awesome opportunities like this one! I'm literally all in - like one hundred and ten percent committed! And I know you feel the same way because, like, I can totally sense your enthusiasm! Let's make this happen and show everyone what we're capable of achieving together!"
        ]
    },
    {
        "user_id": "corporate_buzzword_betty",
        "description": "Excessive corporate jargon and buzzwords",
        "samples": [
            "Let's circle back and touch base to synergize our strategic initiatives moving forward into Q4 and beyond. We need to leverage our core competencies to maximize stakeholder value and ensure we're driving meaningful outcomes across all business verticals. At the end of the day, it's all about creating sustainable growth and fostering innovation that moves the needle on our key performance indicators. I think we should schedule a deep-dive session to really unpack the opportunities and align on our go-forward strategy.",
            "At the end of the day, we need to think outside the box and shift the paradigm to achieve optimal bandwidth utilization across all verticals while maintaining our competitive edge in the marketplace. This is a mission-critical initiative that requires us to be agile and responsive to changing market dynamics. Let's make sure we're all singing from the same hymn sheet and rowing in the same direction as we navigate these uncharted waters and capitalize on low-hanging fruit opportunities.",
            "I'd like to ping you offline to deep-dive into this low-hanging fruit opportunity that's been sitting on our radar for quite some time now. Let's ensure we're all aligned on our north star metrics and that we have full buy-in from all stakeholders before we move the needle on this strategic initiative. We should really leverage our best-in-class solutions to create a win-win scenario that drives value creation across the entire ecosystem and positions us as thought leaders in the space.",
            "We should action this item ASAP to drive ROI and create a win-win scenario that delivers tangible results to our stakeholders. This will really move the needle on our KPIs going forward and demonstrate our commitment to operational excellence and continuous improvement. I'm thinking we need to take this offline and do a comprehensive gap analysis to identify opportunities for optimization and ensure we're maximizing our resource allocation in alignment with our strategic objectives.",
            "Let's take this conversation offline and do a deep-dive to ensure we're all singing from the same hymn sheet on this strategic initiative, yeah? We need to make sure we're leveraging our synergies and creating meaningful touchpoints that drive engagement and foster collaboration across cross-functional teams. This is really about transforming our value proposition and disrupting the market with innovative solutions that resonate with our target demographics. I'm excited to workshop this further and ideate on best practices moving forward!"
        ]
    },
    {
        "user_id": "shakespeare_steve",
        "description": "Shakespearean dramatic language",
        "samples": [
            "Hark! Methinks thy message doth arrive at a most opportune moment, dear colleague! Verily, I have perused thy proposal with great interest and admiration, for it contains such wisdom and foresight as would make the Bard himself weep with joy! Prithee, let us convene anon to discuss the particulars of this most noble undertaking. The stars themselves seem aligned in our favor, and I dare say fortune smiles upon our endeavors!",
            "What light through yonder window breaks? 'Tis the brilliance of thy latest work! I am most thoroughly impressed by the excellence thou hast demonstrated in this project. O, would that all collaborations were blessed with such dedication and skill! Let it be known throughout the land that thy efforts shall not go unrecognized. Forsooth, I shall champion thy cause at the next gathering of our esteemed council!",
            "Alas, the deadline approacheth with the swiftness of Mercury's wings! Yet fear not, dear friend, for we shall meet this challenge as Hercules met his labors - with strength, determination, and unwavering resolve! Though the path ahead be fraught with obstacles, I have the utmost confidence that our combined talents shall overcome all adversity. To arms, to arms! Let us sally forth and conquer this endeavor!",
            "Greetings and salutations, most noble associate! I write to thee with tidings of great import regarding our collaborative enterprise. The progress we have made thus far doth fill my heart with such gladness as the morning sun brings to the darkened sky! Methinks we are on the precipice of something truly magnificent, a achievement that shall echo through the annals of time! Pray tell, when might we meet to discuss the next phase of our grand design?",
            "O frabjous day! Thy latest communication brings me tidings most welcome and fair! I have examined thy proposition with the scrutiny of a scholar and the heart of a poet, and I must proclaim it to be a work of singular merit! Let us not tarry in bringing this vision to fruition, for as the immortal Bard once wrote, 'We know what we are, but know not what we may be!' Together, we shall achieve greatness that transcends the ordinary bounds of mortal enterprise!"
        ]
    },
    {
        "user_id": "yoda_yuki",
        "description": "Yoda-like backwards sentence structure",
        "samples": [
            "Received your message, I have. Most impressed with your work, I am! Great potential in this project, I see. Together, succeed we will. Review the documents tonight, I shall. Strong with this one, the Force is! Patience and dedication, the path to success are. Contact you tomorrow with feedback, I will. Much to discuss, we have. Excited about the possibilities, I am indeed!",
            "Wonderful news, this is! Completed the analysis, our team has. Exceeded our expectations, the results have. Proud of everyone's efforts, I am. Continue on this path, we must. Share the findings with stakeholders next week, we will. Much work ahead lies, but confident in our abilities, I remain. Great things, together we shall accomplish. The project timeline, concerned about I am not.",
            "Hmm, interesting proposal this is! Deep thought, it requires. Meet to discuss further, we should. Many possibilities I see, yes. Careful consideration, such matters demand. Rush into decisions, we must not. Consult with the team, I will. Wisdom comes from patience and reflection, young one. Your insights valuable they are, but explore all options we must first. Call you by end of week, I shall.",
            "Appreciate your patience, I do! Working diligently on your request, the team has been. Challenges we faced, yes, but overcome them we did! Quality over speed, prioritize we must. Ready to present our findings, soon we will be. Impressed you will be, I believe. Hard work and dedication, the foundation of success are. Trust in the process, you must. Disappointed you will not be!",
            "Reached out at the perfect time, you have! Thinking about this very matter, I was. Aligned our thoughts are, it seems. Schedule a meeting this week, we should. Many details to cover, there are. Prepared thoroughly, I am. Surprised by the opportunities, you will be. Exciting times ahead, these are! Forward to our collaboration, I look. Strong potential, in this initiative I sense!"
        ]
    },
    {
        "user_id": "southern_belle_barbara",
        "description": "Sweet Southern hospitality charm",
        "samples": [
            "Well hey there, sugar! I do hope this message finds you doing just wonderfully! Bless your heart for being so patient with all of this - you are just the sweetest thing! I wanted to reach out and let you know that I've been working on your request like there's no tomorrow, and honey, I think you're gonna just love what we've come up with! Now, I know things have been moving slower than molasses in January, but I promise you it'll be worth the wait. Would you be a dear and let me know when you have a moment to chat? I'd be tickled pink to go over everything with you!",
            "Oh my stars! Your latest proposal just knocked my socks clean off! I swear, you have more talent in your little finger than most folks have in their whole body! I've been showing it around the office, and everyone is just absolutely beside themselves with excitement. Honey child, this is exactly what we've been needing! Now listen here, we need to set up a proper meeting to discuss all the wonderful details. How about we grab some sweet tea and really dive into this? I'm happier than a tornado in a trailer park about these possibilities!",
            "Good morning, darlin'! I hope you and yours are doing just fine on this beautiful day! I wanted to touch base with you about the project timeline - now don't you worry your pretty little head about the delay! These things happen, and we're gonna make it right as rain, I promise you that! The team has been working harder than a one-legged cat in a sandbox, and I truly believe we're going to deliver something that'll make your heart sing! Y'all have been such a blessing to work with, and I just can't thank you enough for your understanding and support!",
            "Well, I'll be! Your attention to detail on this project is just phenomenal, honey! I'm more impressed than a chicken with a new pair of shoes! You've gone above and beyond what anyone could've expected, and let me tell you, that does not go unnoticed around here! I've been bragging on you to anyone who'll listen, and they all agree - you're something special! Now, we do need to discuss a few teeny tiny adjustments, but nothing that'll ruffle any feathers. When can we get together and chat about it over some coffee and maybe a slice of my homemade pecan pie?",
            "Hey there, precious! I'm writing to you today with the biggest smile on my face because, honey, we did it! The project is coming together prettier than a peach! I know we've had more ups and downs than a rollercoaster at the state fair, but we persevered, and now look at us! I want to thank you from the bottom of my heart for all your hard work and dedication. You've been sweeter than sweet tea on a hot summer day! Let's plan a celebration - maybe a nice lunch where we can toast to our success? You deserve all the recognition in the world, sugar pie!"
        ]
    }
]


def seed_user(user_data: Dict[str, any]) -> bool:
    """Seed a single user's writing style."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/seed",
            json={
                "user_id": user_data["user_id"],
                "samples": user_data["samples"]
            },
            timeout=30
        )
        response.raise_for_status()
        print(f"✅ Seeded user: {user_data['user_id']} ({user_data['description']})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to seed {user_data['user_id']}: {e}")
        return False


def generate_sample_email(user_id: str, subject: str, prompt: str) -> None:
    """Generate and display a sample email for a user."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json={
                "user_id": user_id,
                "subject": subject,
                "prompt": prompt
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        print(f"\n📧 Sample Email from {user_id}:")
        print(f"Subject: {result['subject']}")
        print(f"{result['body'][:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to generate email for {user_id}: {e}")


def check_api_health() -> bool:
    """Check if the API is running and healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ API Status: {data['status']}")
        print(f"✅ Redis: {data['redis']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ API Health Check Failed: {e}")
        print(f"\nMake sure the server is running:")
        print(f"  docker compose up -d")
        print(f"  OR")
        print(f"  uvicorn server:app --reload")
        return False


def main():
    """Main function to seed demo data."""
    print("=" * 60)
    print("StyleMail Demo Data Seeding Script")
    print("=" * 60)
    print()
    
    # Check API health
    print("Checking API health...")
    if not check_api_health():
        sys.exit(1)
    
    print()
    print(f"Seeding {len(DEMO_USERS)} demo users...")
    print("-" * 60)
    
    success_count = 0
    for user_data in DEMO_USERS:
        if seed_user(user_data):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"Seeding complete: {success_count}/{len(DEMO_USERS)} users seeded successfully")
    print("=" * 60)
    
    # Generate a sample email from each user
    if success_count > 0:
        print()
        print("Generating sample emails to demonstrate different styles...")
        print("-" * 60)
        
        sample_prompt = "Let the team know that we're extending the project deadline by one week"
        
        # Show all users to demonstrate the different styles
        for user_data in DEMO_USERS:
            generate_sample_email(
                user_data["user_id"],
                "Project Update",
                sample_prompt
            )
    
    print()
    print("=" * 60)
    print("✨ Demo data seeding complete!")
    print()
    print("Try the web demo at: http://localhost:8000/static/demo.html")
    print("Or use these user IDs in your API calls:")
    for user_data in DEMO_USERS:
        print(f"  - {user_data['user_id']}: {user_data['description']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
