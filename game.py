"""A gradio application that presents a movie plot using only emoji characters, and asks the user to guess the movie."""

import pydantic
from typing_extensions import Self, ParamSpec, Concatenate
import magentic
import pathlib
import gradio as gr
import random

from typing import Callable, TypeVar

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
    
]


def cache_movie_plot(
    func: Callable[Concatenate[str, P], T],
) -> Callable[Concatenate[str, P], T]:
    def wrapper(title: str, *args: P.args, **kwargs: P.kwargs) -> T:
        """Cache the movie plot."""
        reduced_title = title.lower().replace(" ", "_")
        cache_path = pathlib.Path(f"cache/{reduced_title}.json")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        if cache_path.exists():
            return MoviePlot.model_validate_json(cache_path.read_text(encoding="utf-8"))
        movie_plot = func(title, *args, **kwargs)
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

    @pydantic.field_validator('plot_with_emoji')
    @classmethod
    def remove_redundant_newlines(cls, value):
        return value.replace("\n\n", "\n")



@magentic.chatprompt(
    SYSTEM_PROMPT,
    magentic.UserMessage("The title of the movie is {title}."),
    magentic.UserMessage("Please describe the plot in plaintext, including at least 20 plot beats."),
)
def _from_title_to_plot(title: str) -> str:
    ...

@magentic.chatprompt(
    SYSTEM_PROMPT,
    magentic.UserMessage("The title of the movie is {title}."),
    magentic.UserMessage("The plot of the movie is {plot}."),
    magentic.UserMessage("Please describe the plot using solely emoji. Include at least 30 emoji."),
)
def _from_plot(title: str, plot:str) -> MoviePlot:
    ...

@cache_movie_plot
def from_title(title: str) -> MoviePlot:
    """Create a MoviePlot instance from a movie title.

    Args:
        title: The title of the movie.

    Returns:
        A MoviePlot instance.
    """
    plot = _from_title_to_plot(title)
    return _from_plot(title, plot)
    




def display_real_answer(user_input, title):
    movie_plot = from_title(title)
    return title, movie_plot.plot, movie_plot.plot_with_emoji, movie_plot.explanation


# Gradio interface
def gradio_interface():
    with gr.Blocks() as demo:
        gr.Markdown(f"### Guess the movie plot from the emojis:")
        plot_output = gr.Textbox(label="Plot with Emoji")
        title = gr.State()
        movie_order = gr.State(list(random.sample(MOVIES, len(MOVIES))))

        user_input = gr.Textbox(label="Your Guess")
        with gr.Row():
            real_answer_button = gr.Button("Reveal Movie")
            reset_button = gr.Button("Reset")
        real_answer_output = gr.Textbox(label="Movie Title")
        explanation_output = gr.Textbox(label="Emoji Explanation")
        plot_plaintext_output = gr.Textbox(label="Plot")

        @real_answer_button.click(inputs=[user_input, title], outputs=[
                real_answer_output,
                plot_plaintext_output,
                plot_output,
                explanation_output,
            ])
        def on_real_answer_click(user_input, title):
            real_answer, plot, plot_with_emoji, explanation = display_real_answer(
                user_input, title
            )
            return real_answer, plot, plot_with_emoji, explanation

        @reset_button.click(
            outputs=[
                user_input,
                real_answer_output,
                plot_plaintext_output,
                plot_output,
                explanation_output,
            ],
        )
        def on_reset_click():
            return "", "", "", "", ""


        @reset_button.click(inputs=[movie_order], outputs=[title, plot_output, movie_order])
        @demo.load(inputs=[movie_order], outputs=[title, plot_output, movie_order])
        def get_movie_plot(movie_order):
            if not movie_order:
                return "", "All movies in database exhausted.", []
            title = movie_order[0]
            movie_plot = from_title(title)
            return title, movie_plot.plot_with_emoji, movie_order[1:]

    demo.launch()


if __name__ == "__main__":
    gradio_interface()
