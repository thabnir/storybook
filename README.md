## DnD PvP Mode - AI-Generated Text-Based Adventure/ PvP Game
![faceoff](scratch/image.png)

## Inspiration
The inspiration for DnD PvP Mode stemmed from our love for traditional tabletop role-playing games like Dungeons & Dragons. We wanted to create an immersive and dynamic experience where players could engage in turn-based combat using natural language input, leveraging the power of AI to generate vivid combat art through Dall-E 3.

## What it does
DnD PvP Mode is a text-based adventure and player versus player (PvP) game that brings the magic of Dungeons & Dragons into the digital realm. Two players enter the game from different computers, each choosing their character's name and class. The AI Dungeon Master (DM) takes charge, setting the scene with detailed descriptions of the environment and characters. Players are then free to interact with the world, unleashing their creativity and convincing the DM with their decisions.

The game's core revolves around turn-based combat, where players input their actions and strategies using natural language. The AI DM parses this input, orchestrating a thrilling battle that unfolds in the minds of the players. To enhance the immersive experience, we incorporated Dall-E 3, an AI model that generates stunning combat art based on the DM's descriptions, bringing the characters and scenes to life.

## How we built it
DnD PvP Mode was crafted using Python as the primary programming language. We utilized the OpenAI API for GPT3.5 to power the AI Dungeon Master, enabling it to understand and respond to the players' natural language input. For generating captivating combat art, we integrated Dall-E 3 into the game flow, turning textual descriptions into visually stunning images.

The web interface was developed using Flask for the web server, along with HTML, CSS, and JavaScript to create an intuitive and responsive user experience. This allowed players to seamlessly engage in the game from their respective computers, making decisions, and witnessing the unfolding narrative.

## Challenges we ran into
One of the main challenges we faced was integrating the various components seamlessly. Using GPT functions to parse natural language output and consistently produce quality outputs was a challenging task, but rewarding. Coordinating the communication between the AI Dungeon Master, Dall-E 3, and the web interface required careful planning and implementation, especially to guarantee that each player's client remained in-sync and avoided race conditions. Additionally, ensuring that the generated combat art aligned with the narrative and remained stylistically consistent between prompts posed a creative and technical challenge that required a lot of careful prompt engineering.

## Accomplishments that we're proud of
We are proud to have successfully created a dynamic and immersive gaming experience that blends traditional tabletop RPG elements with cutting-edge AI technology. The ability to let players express their creativity and witness AI-generated combat art in real-time is a significant achievement for our team.

## What we learned
Throughout the development process, we gained valuable insights into leveraging AI for interactive storytelling and visual art generation. The integration of GPT3.5 and Dall-E 3 required a deep understanding of both technologies, and we are excited to continue exploring their potential in future projects.

## What's next for DnD PvP Mode
The journey doesn't end here! In the future, we plan to expand DnD PvP Mode by incorporating more status features, classes, and environments. We aim to enhance the AI Dungeon Master's capabilities with a broader range of functions to call, allowing for even more intricate and personalized storytelling and statuses that it may inflict upon the players. In future, we may also be able to create stable characters which the AI art generation models may be able to recreate in each scene. Stay tuned for more adventures in the world of DnD PvP Mode!

![duel](scratch/image2.png)
