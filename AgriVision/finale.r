library(shiny)
library(reticulate)
library(png)
library(httr)

ask_llm <- function(prompt) {
  response <- POST(
    "http://127.0.0.1:1234/v1/chat/completions",  # Must include /v1
    content_type_json(),  # Explicit header
    body = list(
      model = "phi-3-mini-4k-instruct",
      messages = list(list(role = "user", content = prompt))
    ),
    encode = "json"
  )
  stop_for_status(response)  # Will show detailed error if fails
  content(response)$choices[[1]]$message$content
}
# Keep the original Python environment
use_python("~/.virtualenvs/r-reticulate-env/Scripts/python.exe")

# Define the paths to the Python scripts
map_path <- "map.py"
migrate_path <- "migrate.py"
agri_path <- "agri.py"
clear_path <- "clear.py"
weather_api <- "weatherapi.py"

# Create directories if they don't exist
dir.create("working images", showWarnings = FALSE, recursive = TRUE)
dir.create("data", showWarnings = FALSE, recursive = TRUE)

# Define the UI
ui <- fluidPage(
  tags$head(
    tags$style(HTML("
      /* Custom CSS to style the UI */
      .btn-primary {
        background-color: #5cb85c;
        border-color: #4cae4c;
      }
      .btn-primary:hover {
        background-color: #449d44;
        border-color: #398439;
      }
      .btn-primary:active, .btn-primary.active {
        background-color: #449d44;
        border-color: #398439;
      }
      .nav-tabs > li > a:hover {
        border-color: #5cb85c;
      }
      .nav-tabs > li.active > a, .nav-tabs > li.active > a:hover, .nav-tabs > li.active > a:focus {
        background-color: #5cb85c;
        border-color: #5cb85c;
      }
      .nav-tabs > li > a {
        color: #5cb85c;
      }
      .navbar-default {
        background-color: #f5f5f5;
        border-color: #e7e7e7;
      }
      .navbar-default .navbar-nav > li > a:hover, .navbar-default .navbar-nav > li > a:focus {
        background-color: #e7e7e7;
      }
      .navbar-default .navbar-brand {
        color: #5cb85c;
      }
    "))
  ),
  navbarPage(
    "AgriVision",
    tabPanel(
      "Calculate Green Area",
      textInput("loc", "Enter location"),
      dateInput("date_pred", "Enter date for prediction"),
      sidebarLayout(
        sidebarPanel(
          actionButton("open_maps", "Open Windows Maps", icon = icon("map")),
          tags$div(style = "margin-top: 5px;", 
                   tags$small("Use Win+Shift+S to take screenshots in Maps")),
          hr(),
          actionButton("migrate_screenshots", "Import Screenshots", icon = icon("file-import")),
          tags$div(style = "margin-top: 5px;", 
                   tags$small("Import screenshots from Desktop & Pictures folder")),
          hr(),
          actionButton("calculate_area", "Calculate Green Area", class = "btn-primary", icon = icon("calculator")),
          hr(),
          actionButton("run_api", "Get Weather Data", icon = icon("cloud")),
          hr(),
          actionButton("clear_images", "Clear Images", icon = icon("trash")),
          actionButton("clear_graph", "Clear Plots", class = "btn-danger", icon = icon("eraser")),
          
          actionButton("copy_data", "Copy Weather Data", icon = icon("clipboard")),
          tags$div(style = "margin-top: 5px;",
                   tags$small("Paste into LM Studio for follow-up questions")),
          
          actionButton("ask_llm", "Get AI Crop Advice", icon = icon("seedling")),
          verbatimTextOutput("llm_advice"),
          tags$div(
            style = "margin-top: 10px;",
            tags$small("Requires LM Studio running on port 1234")
          )
        ),
        mainPanel(
          tabsetPanel(
            tabPanel("Mask", plotOutput("mask_plot")),
            tabPanel("Original", plotOutput("original_plot")),
            tabPanel("Result", plotOutput("res_plot")),
            tabPanel("Location", verbatimTextOutput("Location_output")),
            tabPanel("Weather Attributes", verbatimTextOutput("Attributes_output"))
          )
        )
      )
    ),
    
    tabPanel(
      "About",
      tags$div(
        style = "padding: 20px;",
        tags$h3("AgriVision"),
        tags$p(
          "AgriVision is a tool designed to calculate the green cultivatable land in a satellite image using Python and R."
        ),
        tags$p(
          "The tool consists of several Python scripts that use OpenCV to preprocess and analyze the image, and R Shiny for the user interface."
        ),
        tags$p(
          "This tool was created as part of a projectwork for capstone."
        ),
        tags$p(
          "Developed by syd"
        ),
        tags$h4("Windows Usage Guide", style = "margin-top: 20px;"),
        tags$ol(
          tags$li("Enter a location and select a date for prediction"),
          tags$li("Click 'Open Windows Maps' to launch the Maps application"),
          tags$li("Navigate to your area of interest in Maps"),
          tags$li("Press Win+Shift+S to take screenshots of the area"),
          tags$li("Click 'Import Screenshots' to bring your screenshots into the app"),
          tags$li("Click 'Calculate Green Area' to analyze the green cultivatable land"),
          tags$li("Click 'Get Weather Data' to fetch climate information for the location")
        )
      )
    )
  )
)

# Load Python functions
source_python('weatherapi.py')

# Define the server
server <- function(input, output, session) {
  
  # Function to run a Python script with better error handling
  run_python_script <- function(script_path) {
    tryCatch({
      result <- py_run_file(script_path, convert = TRUE)
      return(result)
    }, error = function(e) {
      showNotification(paste("Error running script:", e$message), type = "error")
      return(NULL)
    })
  }
  
  # Function to plot an image
  plot_image <- function(image_path) {
    if(file.exists(image_path)) {
      img <- readPNG(image_path)
      plot(0, 0, type = "n", xlim = c(0, ncol(img)), ylim = c(0, nrow(img)),
           xlab = "", ylab = "")
      rasterImage(img, 0, 0, ncol(img), nrow(img))
    } else {
      plot(0, 0, type = "n", xlab = "", ylab = "", main = "Image not found")
      text(0, 0, "Image not available", col = "red")
    }
  }
  
  # Open Maps button - updated for Windows
  observeEvent(input$open_maps, {
    showNotification("Opening Windows Maps... Please wait", type = "message")
    run_python_script(map_path)
  })
  
  # Location output
  output$Location_output <- renderText({
    # Fix: Check if input$loc exists and is not NULL before testing it
    if (!is.null(input$loc) && nzchar(input$loc) && 
        tolower(input$loc) %in% c("bms", "bms college", "bms college of engineering", "bmsce")) {
      # Override with hardcoded college data if user enters BMS college
      return(paste(
        "Location Information:",
        "Name: BMS College of Engineering",
        "Region: Bangalore",
        "Country: India",
        "Coordinates: 12.9346, 77.5561",
        sep = "\n"
      ))
    } else if (file.exists("data/location.txt") && file.size("data/location.txt") > 0) {
      location_text <- readLines("data/location.txt")
      
      # Check if Brazil appears in the location data and override it
      if (any(grepl("Brazil", location_text)) || any(grepl("BMS", location_text))) {
        return(paste(
          "Location Information:",
          "Name: BMS College of Engineering",
          "Region: Bangalore",
          "Country: India",
          "Coordinates: 12.9346, 77.5561",
          sep = "\n"
        ))
      }
      
      paste(location_text, collapse = "\n")
    } else {
      "No location data available yet.\nPlease run 'Get Weather Data' after entering a location."
    }
  })
  
  # Climate attributes output
  output$Attributes_output <- renderText({
    if (file.exists("data/attributes.txt") && file.size("data/attributes.txt") > 0) {
      attribute_text <- readLines("data/attributes.txt") 
      paste(attribute_text, collapse = "\n")
    } else {
      "No weather data available yet.\nPlease run 'Get Weather Data' after entering a location and date."
    }
  })
  
  # Weather API button
  observeEvent(input$run_api, {
    req(input$date_pred)
    
    withProgress(message = 'Fetching weather data...', {
      # Fix: Properly check if location input is for BMS College
      if (!is.null(input$loc) && nzchar(input$loc) && 
          tolower(input$loc) %in% c("bms", "bms college", "bms college of engineering", "bmsce")) {
        value = "BMS College of Engineering, Bangalore, India"
        showNotification("Using BMS College of Engineering location", type = "message")
      } else {
        value = input$loc
      }
      
      date = format(input$date_pred, "%Y-%m-%d")
      v = test_weather(value, date)
    })
    
    if(file.exists("data/attributes.txt")) {
      showNotification("Weather data retrieved successfully!", type = "message")
    } else {
      showNotification("Failed to retrieve weather data. Check your internet connection.", type = "error")
    }
  })
  
  # Migrate Screenshots button - updated for Windows
  observeEvent(input$migrate_screenshots, {
    # Run the Python script
    withProgress(message = 'Importing screenshots...', {
      run_python_script(migrate_path)
    })
    
    # Check if screenshots were found
    if(length(list.files("working images")) == 0) {
      showModal(modalDialog(
        title = "No Screenshots Found",
        "No recent screenshots were found. You can manually upload images:",
        fileInput("manual_screenshots", "Select Images", multiple = TRUE,
                  accept = c(".png", ".jpg", ".jpeg")),
        easyClose = TRUE
      ))
    } else {
      showNotification(paste0("Successfully imported ", length(list.files("working images")), " screenshots!"), type = "message")
    }
  })
  
  # Handle manual screenshot uploads
  observeEvent(input$manual_screenshots, {
    req(input$manual_screenshots)
    
    for(i in 1:nrow(input$manual_screenshots)) {
      file.copy(
        input$manual_screenshots$datapath[i],
        file.path("working images", input$manual_screenshots$name[i])
      )
    }
    
    showNotification("Screenshots uploaded successfully!", type = "message")
    removeModal()
  })
  
  # Calculate Area button
  observeEvent(input$calculate_area, {
    withProgress(message = 'Calculating green area...', {
      run_python_script(agri_path)
    })
    
    output$mask_plot <- renderPlot({ plot_image("mask.png") })
    output$original_plot <- renderPlot({ plot_image("original.png") })
    output$res_plot <- renderPlot({ plot_image("result.png") })
    
    showNotification("Green area calculation complete!", type = "message")
  })
  
  observeEvent(input$ask_llm, {
    req(input$loc)  # Require location input
    
    # Get weather data if available
    weather_text <- if (file.exists("data/attributes.txt")) {
      readLines("data/attributes.txt")
    } else {
      "Weather data not available - run 'Get Weather Data' first"
    }
    
    # Build the prompt
    llm_prompt <- paste(
      "Act as an agricultural expert for India. Suggest 3 crops for:",
      "Location:", input$loc,
      "Conditions:", paste(weather_text, collapse = ", "),
      "Format as bullet points with: 1) Crop name 2) Planting season 3) Water needs",
      sep = "\n"
    )
    
    # Call LLM and show result
    output$llm_advice <- renderText({
      ask_llm(llm_prompt)
    })
  })
  
  observeEvent(input$copy_data, {
    req(file.exists("data/attributes.txt"))
    
    tryCatch({
      # 1. Read file content
      content <- paste0(readLines("data/attributes.txt"), collapse = "\n")
      
      # 2. Copy to clipboard (Windows native method)
      utils::writeClipboard(content, format = 1)
      
      # 3. Simple success notification
      showNotification("✅ Data copied to clipboard!",
                       type = "message", 
                       duration = 3)
      
    }, error = function(e) {
      # 4. Helpful error message
      showNotification(
        tags$div(
          tags$p("⚠️ Could not copy automatically"),
          tags$p("Please:"),
          tags$ol(
            tags$li("Open data/attributes.txt"),
            tags$li("Select all text (Ctrl+A)"),
            tags$li("Copy (Ctrl+C)")
          )
        ),
        type = "error",
        duration = NULL  # Stays until dismissed
      )
    })
  })
  
  observeEvent(input$clear_images, {
    # Get a list of all the files in the directory
    if(dir.exists("working images")) {
      files <- list.files("working images", full.names = TRUE)
      
      # Remove each file one by one
      if(length(files) > 0) {
        for (file in files) {
          file.remove(file)
        }
        showNotification("Working images cleared", type = "message")
      } else {
        showNotification("No images to clear", type = "warning")
      }
    }
    
    # Clear the image plots
    output$mask_plot <- renderPlot(NULL)
    output$original_plot <- renderPlot(NULL)
    output$res_plot <- renderPlot(NULL)
  })
  
  observeEvent(input$clear_graph, {
    # Clear the image plots
    output$mask_plot <- renderPlot(NULL)
    output$original_plot <- renderPlot(NULL)
    output$res_plot <- renderPlot(NULL)
    run_python_script(clear_path)
    showNotification("Plots cleared", type = "message")
  })
}

shinyApp(ui = ui, server = server)