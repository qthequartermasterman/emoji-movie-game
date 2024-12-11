"""A gradio application that presents a movie plot using only emoji characters, and asks the user to guess the movie.

To run, simply run this script, which will start the Gradio interface.

```bash
python game.py
```

Then navigate to the URL provided in the terminal to play the game.

The game will present a movie plot using only emoji characters, and ask the user to guess the movie. The user can input
their guess, and then click the "Reveal Movie" button to see the actual movie title, the plot in plain text, and the
explanation of the emoji plot.

The user can then click the "Reset" button to move on to the next movie plot.

Because of the time it takes to generate the emoji plot for each movie (using the OpenAI API), it can sometimes
take a few seconds to load the next movie plot. The user can see the loading spinner while the next movie plot is being
generated.
"""

import pydantic
from typing_extensions import ParamSpec, Concatenate
import magentic
import pathlib
import gradio as gr
import random
import asyncio

from typing import Callable, TypeVar, Awaitable

T = TypeVar("T")
P = ParamSpec("P")

SYSTEM_PROMPT = magentic.SystemMessage(
    "You are an expert cinematographer, director, and script writer. You have been tasked with summarizing a "
    "movie plot using only emoji characters. You must also provide an explanation of the plot with emoji, i.e. "
    "what the emoji represent. You may use any emoji you like, but you must use at least 5 emoji characters."
    " You may not use any plain text in the plot with emoji."
    " Your emoji plot should be as thorough as possible, with as many plot points as possible represented in the"
    " emoji. Include at least 30 emoji representing plot points."
)

MOVIES = [
    "Star Wars: Episode IV - A New Hope",
    "Dune",
    "Elf",
    "17 Miracles",
    "The Princess Bride",
    "Inception",
    "Avatar (2009)",
    "The Lion King",
    "The Lord of the Rings: The Fellowship of the Ring",
    "Finding Nemo",
    "Shrek",
    "Over the Hedge",
    "The Bee Movie",
    "Home Alone 2",
    "The Incredibles",
    "The Last Starfighter",
    "Beetlejuice",
    "The Dark Knight",
    "Forrest Gump",
    "Star Wars: Episode V - The Empire Strikes Back",
    "Interstellar",
    "Titanic",
    "It's a Wonderful Life",
    "Back to the Future",
    "Wall-e",
    "Indiana Jones and the Raiders of the Lost Ark",
    "Avengers: Infinity War",
    "Avengers: Endgame",
    "The Sound of Music",
    "Avengers: Age of Ultron",
    "The Avengers",
    "Spider-Man: Into the Spider-Verse",
    "Spider-Man",
    "Spider-Man 2",
    "Spider-Man 3",
    "Spider-Man: No Way Home",
    "Coco",
    "Toy Story",
    "Toy Story 2",
    "2001: A Space Odyssey",
    "Citizen Kane",
    "Jaws",
    "Jurassic Park",
    "Up",
    "Top Gun",
    "The Great Escape",
    "Mary Poppins",
    "The Wizard of Oz",
    "Inside Out",
    "Now You See Me",
    "Harry Potter and the Sorcerer's Stone",
    "Harry Potter and the Chamber of Secrets",
    "Monsters, Inc.",
    "How to Train Your Dragon",
    "Pirates of the Caribbean: The Curse of the Black Pearl",
    "Stand and Deliver",
    "Groundhog Day",
    "Cars",
    "The Prince of Egypt",
    "The Polar Express",
    "The Nightmare Before Christmas",
    "The Little Mermaid",
    "Beauty and the Beast",
    "Aladdin",
    "The Jungle Book",
    "Hercules",
    "Mulan",
    "Tarzan",
    "The Emperor's New Groove",
    "Chicken Run",
    "Monsters vs. Aliens",
    "Megamind",
    "Madagascar",
    "Kung Fu Panda",
    "Bolt",
    "Ready Player One",
    "Big Hero 6",
    "Rudolph the Red-Nosed Reindeer",
    "A Charlie Brown Christmas",
    "How the Grinch Stole Christmas",
    "The Muppet Christmas Carol",
    "The Santa Clause",
    "Twister",
    "Independence Day",
    "The Day After Tomorrow",
    "The Core",
    "The Martian",
    "The Hunger Games",
    "Frozen",
    "E.T. the Extra-Terrestrial",
    "The Goonies",
    "Night at the Museum",
    "The Chronicles of Narnia: The Lion, the Witch and the Wardrobe",
    "Star Trek: The Motion Picture",
    "Star Trek II: The Wrath of Khan",
    "Star Trek V: The Final Frontier",
    "Space Jam",
    "Stargate",
    "Galaxy Quest",
    "The Hitchhiker's Guide to the Galaxy",
    "Casino Royale",
    "Contact",
    "Transformers",
    "Guardians of the Galaxy",
    "Deep Impact",
    "Armageddon",
    "Star Wars: Episode I - The Phantom Menace",
    "Mission: Impossible",
    "The Bourne Identity",
    "21",
    "Ocean's Eleven",
    "The Italian Job",
    "The Fast and the Furious",
    "Passengers",
    "Gravity",
    "Spaceballs",
    "Apollo 13",
    "The Greatest Game Ever Played",
    "The Blind Side",
    "Remember the Titans",
    "The Rookie",
    "The Mighty Ducks",
    "Air Bud",
    "The Sandlot",
    "The Karate Kid",
    "Rise of the Planet of the Apes",
    "Dawn of the Planet of the Apes",
    "War for the Planet of the Apes",
    "Ender's Game",
    "Treasure Planet",
    "Flash Gordon",
    "Zathura: A Space Adventure",
    "The Lego Movie",
    "Battlestar Galactica",
    "Buck Rogers in the 25th Century",
    "Gremilns",
    "Green Lantern",
    "Ghost Rider",
    "Ghostbusters",
    "The Truman Show",
    "Knives Out",
    "The Fifth Element",
    "The Sixth Sense",
    "500 Days of Summer",
    "Jumanji",
    "A Knight's Tale",
    "School of Rock",
    "Mamma Mia!",
    "The Greatest Showman",
    "Mrs. Doubtfire",
    "The Parent Trap",
    "Freaky Friday",
    "Coraline",
    "Dodgeball: A True Underdog Story",
    "Napoleon Dynamite",
    "Ferris Bueller's Day Off",
    "Dirty Dancing",
    "Footloose",
    "Monty Python and the Holy Grail",
    "X-Men",
    "Thor",
    "Pearl Harbor",
    "Gattaca",
    "Labrynth",
    "Fantastic Mr. Fox",
    "Who Framed Roger Rabbit",
    "Ice Age",
    "Little Shop of Horrors",
    "Hocus Pocus",
    "The Incredible Hulk",
    "Big Trouble in Little China",
    "Atlantis: The Lost Empire",
    "The Corpse Bride",
    "The Day the Earth Stood Still",
    "The West Side Story",
]


def cache_file_path(title: str) -> pathlib.Path:
    reduced_title = title.lower().replace(" ", "_")
    return pathlib.Path(f"cache/{reduced_title}.json")


ALREADY_CACHED_MOVIES = [movie for movie in MOVIES if cache_file_path(movie).exists()]


def cache_movie_plot(
    func: Callable[Concatenate[str, P], Awaitable[T]],
) -> Callable[Concatenate[str, P], Awaitable[T]]:
    async def wrapper(title: str, *args: P.args, **kwargs: P.kwargs) -> T:
        """Cache the movie plot."""
        cache_path = cache_file_path(title)
        if cache_path.exists():
            return MoviePlot.model_validate_json(cache_path.read_text(encoding="utf-8"))
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        movie_plot = await func(title, *args, **kwargs)
        assert isinstance(movie_plot, MoviePlot)
        cache_path.write_text(movie_plot.model_dump_json(indent=2), encoding="utf-8")
        return movie_plot

    return wrapper


class MoviePlot(pydantic.BaseModel):
    title: str = pydantic.Field(..., title="Title of the movie")
    plot: str = pydantic.Field(
        ..., title="Plot of the movie, described in plain text without emoji"
    )
    plot_with_emoji: str = pydantic.Field(
        ...,
        title=(
            "Plot of the movie, described solely with emoji (no plain text). Be as thorough as possible. As many plot"
            " points as possible should be represented in the emoji."
        ),
    )
    explanation: str = pydantic.Field(
        ..., title="Explanation of the plot with emoji, i.e. what the emoji represent"
    )

    @pydantic.field_validator("plot_with_emoji")
    @classmethod
    def remove_redundant_newlines(cls, value):
        return value.replace("\n\n", "\n")


@magentic.chatprompt(
    SYSTEM_PROMPT,
    magentic.UserMessage("The title of the movie is {title}."),
    magentic.UserMessage(
        "Please describe the plot in plaintext, including at least 12 plot beats."
    ),
)
async def _from_title_to_plot(title: str) -> str: ...


@magentic.chatprompt(
    SYSTEM_PROMPT,
    magentic.UserMessage("The title of the movie is {title}."),
    magentic.UserMessage("The plot of the movie is {plot}."),
    magentic.UserMessage(
        "Please describe the plot using solely emoji. Include at least 30 emoji."
    ),
)
async def _from_plot(title: str, plot: str) -> MoviePlot: ...


@cache_movie_plot
async def from_title(title: str) -> MoviePlot:
    """Create a MoviePlot instance from a movie title.

    Args:
        title: The title of the movie.

    Returns:
        A MoviePlot instance.
    """
    plot = await _from_title_to_plot(title)
    return await _from_plot(title, plot)


async def display_real_answer(user_input, title):
    movie_plot = await from_title(title)
    return title, movie_plot.plot, movie_plot.plot_with_emoji, movie_plot.explanation


# Gradio interface
def gradio_interface():
    with gr.Blocks(css=".emoji-text textarea {font-size: 26px !important}") as demo:
        gr.Markdown("### Guess the Movie Title from the Plot Explained with Emoji:")
        plot_output = gr.Textbox(label="Plot with Emoji", elem_classes="emoji-text")
        title = gr.State()
        movie_title_queue = gr.State(list(random.sample(MOVIES, len(MOVIES))))
        next_movie_plot_task = gr.State(None)

        user_input = gr.Textbox(label="Your Guess")
        with gr.Row():
            real_answer_button = gr.Button("Reveal Movie")
            reset_button = gr.Button("Reset")
        real_answer_output = gr.Textbox(label="Movie Title")
        explanation_output = gr.Textbox(label="Emoji Explanation")
        plot_plaintext_output = gr.Textbox(label="Plot")

        @real_answer_button.click(
            inputs=[user_input, title],
            outputs=[
                real_answer_output,
                plot_plaintext_output,
                plot_output,
                explanation_output,
            ],
        )
        async def on_real_answer_click(user_input, title):
            real_answer, plot, plot_with_emoji, explanation = await display_real_answer(
                user_input, title
            )
            return real_answer, plot, plot_with_emoji, explanation

        @reset_button.click(
            outputs=[
                user_input,
                real_answer_output,
                plot_plaintext_output,
                explanation_output,
            ],
        )
        def on_reset_click():
            return "", "", "", ""

        @demo.load(
            inputs=[movie_title_queue, next_movie_plot_task],
            outputs=[title, plot_output, movie_title_queue, next_movie_plot_task],
        )
        async def initialize_first_movie_plot(movie_order, next_movie_plot_task):
            if ALREADY_CACHED_MOVIES:
                title = random.choice(ALREADY_CACHED_MOVIES)
                movie_order.remove(title)
            else:
                title = movie_order.pop(0)
            next_movie_plot_task = (title, asyncio.create_task(from_title(title)))
            return await get_movie_plot(movie_order, next_movie_plot_task)

        @reset_button.click(
            inputs=[movie_title_queue, next_movie_plot_task],
            outputs=[title, plot_output, movie_title_queue, next_movie_plot_task],
        )
        async def get_movie_plot(
            movie_order, next_movie_plot_task: tuple[str, Awaitable] | None
        ):
            if not movie_order:
                return "", "All movies in database exhausted.", [], None

            original_title, movie_plot_task = next_movie_plot_task

            movie_plot = await movie_plot_task

            new_title = movie_order.pop(0)
            new_movie_plot_task = asyncio.create_task(from_title(new_title))

            return (
                original_title,
                movie_plot.plot_with_emoji,
                movie_order,
                (new_title, new_movie_plot_task),
            )

    demo.launch()


if __name__ == "__main__":
    with magentic.OpenaiChatModel(model="gpt-4o-mini"):
        gradio_interface()
