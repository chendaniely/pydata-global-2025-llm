from pathlib import Path

import chatlas
import plotly.express as px
import querychat
import seaborn as sns
from ridgeplot import ridgeplot
from shiny import reactive
from shiny.express import render, ui
from shinywidgets import render_plotly, render_widget

tips = sns.load_dataset("tips")

greeting = Path(__file__).parent / "greeting.md"
data_desc = Path(__file__).parent / "data_description.md"


def use_github_models(system_prompt: str) -> chatlas.Chat:
    # GitHub models give us free rate-limited access to the latest LLMs
    # you will need to have GITHUB_PAT defined in your environment
    # return chatlas.ChatGithub(
    #     model="gpt-4.1",
    #     system_prompt=system_prompt,
    # )
    return chatlas.ChatOpenAI(
        system_prompt=system_prompt,
    )


qc_config = querychat.init(
    tips,
    "tips",
    greeting=greeting,
    data_description=data_desc,
    client=use_github_models,
)

qc = querychat.server("chat", qc_config)


# title
ui.page_opts(title="Restaurant tipping", fillable=True)

# sidebar
querychat.sidebar("chat")


@reactive.calc
def filtered_data():
    return qc.df()


with ui.layout_columns():

    @render.text
    def current_query():
        return qc.sql() or "SELECT * FROM tips"


with ui.layout_columns(fill=False):
    with ui.value_box():
        "Total tippers"

        @render.text
        def total_tippers():
            return filtered_data().shape[0]

    with ui.value_box():
        "Average tip"

        @render.text
        def average_tip():
            perc = filtered_data().tip / filtered_data().total_bill
            return f"{perc.mean():.1%}"

    with ui.value_box():
        "Average bill"

        @render.text
        def average_bill():
            bill = filtered_data().total_bill.mean()
            return f"${bill:.2f}"


# second row of cards
with ui.layout_columns(col_widths=[6, 6]):
    with ui.card(full_screen=True):
        ui.card_header("Tips data")

        @render.data_frame
        def tips_data():
            return filtered_data()

    with ui.card(full_screen=True):
        ui.card_header("Total bill vs tip")

        @render_plotly
        def scatterplot():
            return px.scatter(
                filtered_data(), x="total_bill", y="tip", trendline="lowess"
            )


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Tip percentages")

        @render_widget
        def ridge():
            filtered_data()["percent"] = (
                filtered_data().tip / filtered_data().total_bill
            )

            uvals = filtered_data().day.unique()
            samples = [
                [filtered_data().percent[filtered_data().day == val]]
                for val in uvals
            ]

            plt = ridgeplot(
                samples=samples,
                labels=uvals,
                bandwidth=0.01,
                colorscale="viridis",
                colormode="row-index",
            )

            plt.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                )
            )

            return plt
