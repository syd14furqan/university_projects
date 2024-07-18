#install these libs
"""!apt-get -qq install -y graphviz libgraphviz-dev pkg-config
!pip install pygraphviz
!pip install graphviz"""

import pygraphviz as pgv
import tempfile
import os

def create_activity_diagram(scenario):
    # Create a PyGraphviz AGraph object
    diagram = pgv.AGraph(directed=True)

    # Split the scenario into activities
    activities = scenario.split(';')

    # Add activities to the diagram
    for activity in activities:
        diagram.add_node(activity.strip())

    # Connect activities in sequence
    for i in range(len(activities) - 1):
        diagram.add_edge(activities[i].strip(), activities[i + 1].strip(), label='')

    # Save the diagram to a temporary directory
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "activity_diagram")
    diagram.draw(file_path + '.png', format='png', prog='dot')

    print(f"Activity diagram saved to: {file_path}.png")

"""if __name__ == "__main__":
    # Example with a different scenario
    custom_scenario = "Start; Receive Customer Order; Process Order Details; Prepare Items; Ship Order; End"

    # Create and display the activity diagram
    create_activity_diagram(custom_scenario)


  if __name__ == "__main__":
    # Example with a different scenario
    custom_scenario = "Start; Receive Customer Order; Process Order Details; Prepare Items; Ship Order; End"

    # Create and display the activity diagram
    create_activity_diagram(custom_scenario)"""


if __name__ == "__main__":
    # Example with an "if" condition scenario
    scenario_with_if = "Start; Define Requirements; Design System; Implement Code; \
                        if (Code has Bugs) then { Fix Bugs; Test Again; } else { Test System; } \
                        Deploy System; End"

    # Create and display the activity diagram
    create_activity_diagram(scenario_with_if)
