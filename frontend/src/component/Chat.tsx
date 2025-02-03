import React, { useState, useEffect, useRef } from "react";
import { chatController } from "../controller/chatController";
import { ChatData, ChatHistory, LocationItem } from "../model/Chat";
import { getAuth, onAuthStateChanged } from "firebase/auth";
import ReactMarkdown from "react-markdown";
import MapComponent from './MapComponent';




const Chat: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [mode, setMode] = useState("basic");
  const [welcomeMessageSent, setWelcomeMessageSent] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showSidebar, setShowSidebar] = React.useState(false);
  const [faqContent, setFaqContent] = useState<{ ques: string; answer: string }[] | false>(false);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null); // To track expanded FAQ
  const [mapVisible, setMapVisible] = useState(false); // Controls map visibility
  const [mapCoordinates, setMapCoordinates] = useState<{ lat1: number;
    lng1: number;
    lat2: number;
    lng2: number; } | null>(null);
  const [isTyping, setIsTyping] = useState(false);

  
  type Message = {
    text?: string | null; // Optional plain text
    richContent?: JSX.Element[]; // Optional JSX for rich content
    sender: "user" | "bot";
};

  const chatBodyRef = useRef<HTMLDivElement>(null);

  // Simulate Typing Indicator Effect
  useEffect(() => {
    if (isTyping) {
      console.log("Typing indicator on");
    } else {
      console.log("Typing indicator off");
    }
  }, [isTyping]);
  
  

  


  // Monitor authentication state
  useEffect(() => {
    const auth = getAuth();
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      const loggedIn = !!user;
      setIsAuthenticated(!!user); // Set to true if user exists, false otherwise

      // Automatically hide the sidebar if the user logs out
      if (!loggedIn) {
      }
    });
    return () => unsubscribe();
  }, []);

  const toggleChat = () => setIsOpen(!isOpen);

  const fetchFAQs = () => {
    if (!faqContent) {
      console.log("Fetching FAQs...");

      chatController.getFAQs()
        .then((faqs) => {
          setFaqContent(faqs); // Update state with FAQ array
        })
        .catch((error) => {
          console.error("Error fetching FAQs:", error);
          setFaqContent(false); // Reset FAQ state on error
        });
    }
  };

  const toggleExpandFAQ = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index); // Toggle expand/collapse
  };
  

  const getLocation = (): Promise<{ lat: number; lng: number }> => {
    return new Promise((resolve, reject) => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            resolve({ lat: position.coords.latitude, 
                      lng: position.coords.longitude });
          },
          (error) => reject(error),
          { timeout: 10000 }
        );
      } else {
        reject("Geolocation is not supported by this browser.");
      }
    });
  };

  const openMap = (lat1: number, lng1: number, lat2: number, lng2: number) => {
    setMapCoordinates({ lat1, lng1, lat2, lng2 });
    setMapVisible(true);
  };

  const closeMap = () => {
    setMapVisible(false);
    setMapCoordinates(null);
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;
  
    try {
      // Show "Typing..." indicator
      setIsTyping(true);
  
      // Add user message to chat
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: newMessage, sender: "user", timestamp: new Date().toISOString() },
      ]);
  
      setNewMessage(""); // Clear the input field
  
      // Simulate backend processing with "Typing..."
      const location = await getLocation().catch((error) => {
        console.error("Error getting location:", error);
        throw new Error("Unable to fetch location. Please enable location services.");
      });
  
      const chat: ChatData = {
        inputText: newMessage.trim(),
        latitude: location.lat,
        longitude: location.lng,
        mode,
      };
  
      console.log("Chat Data Sent to Backend:", chat);
  
      // Fetch response from the backend
      const response = await chatController.getChatResponse(chat);
      console.log("Full Backend Response:", response);
  
      // Add chatbot response to chat
      const { message, map_url, msg, mode: responseMode } = response.data;
  
      setIsTyping(false); // Hide "Typing..." indicator
  
      if (responseMode === "location" && Array.isArray(msg)) {
        handleLocationResponse(msg, location);
      } else if (map_url) {
        handleMapUrlResponse(map_url, message);
      } else if (message) {
        handleTextResponse(message);
      } else {
        throw new Error("Unexpected response format.");
      }
    } catch (error) {
      console.error("Error sending message or fetching response:", error);
  
      setIsTyping(false); // Hide "Typing..." indicator
  
      // Add error message to chat
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          text: "Sorry, something went wrong. Please try again.",
          sender: "bot",
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  };
  
  
  // Handle location-based responses
  const handleLocationResponse = (
    locations: LocationItem[], // Type explicitly as an array of LocationItem
    userLocation: { lat: number; lng: number } // Define userLocation structure
  ) => {
    const locationArray = Object.values(locations) as LocationItem[];
    console.log("Location Array:", locationArray);
  
    const botResponse = locationArray.map((item, index) => (
      <div
        key={index}
        style={{
          border: "1px solid #aaa",
          color: "#222",
          marginBottom: "16px",
          padding: "16px 24px",
          borderRadius: "12px",
          backgroundColor: "#e8f5e9",
          boxShadow: "0 6px 12px rgba(0, 0, 0, 0.15)",
          transition: "transform 0.3s ease, box-shadow 0.3s ease",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          maxWidth: "400px",
        }}
      >
        <h4 style={{ margin: "0 0 12px", fontSize: "22px", fontWeight: "bold", color: "#1b5e20" }}>
          {item.name}
        </h4>
        <p style={{ margin: "0 0 12px", fontSize: "16px", color: "#4e4e4e" }}>
          Distance: <strong>{item.distance}</strong>
        </p>
        <button
          onClick={() => openMap(userLocation.lat, userLocation.lng, parseFloat(item.latitude), parseFloat(item.longitude))}
          style={{
            background: "#2e7d32",
            color: "#fff",
            border: "none",
            padding: "8px 14px",
            borderRadius: "6px",
            cursor: "pointer",
            fontWeight: "bold",
            fontSize: "14px",
            transition: "background 0.3s ease",
          }}
        >
          Show on Map
        </button>
      </div>
    ));
  
    setMessages((prevMessages) => [
      ...prevMessages,
      { text: `I found ${locationArray.length} location(s) for you:`, sender: "bot", timestamp: new Date().toISOString() },
      { text: null, richContent: botResponse, sender: "bot", timestamp: new Date().toISOString() },
    ]);
  };
  
  // Handle map URL responses
  const handleMapUrlResponse = (map_url: string, message: string) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { text: message || "Here is the map for your directions:", sender: "bot", timestamp: new Date().toISOString() },
      { text: map_url, sender: "bot", timestamp: new Date().toISOString() },
    ]);
  };
  
  // Handle text-based responses
  const handleTextResponse = (message: string) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { text: message, sender: "bot", timestamp: new Date().toISOString() },
    ]);
  };

  const handleButtonClick = (option: string) => {
    setMode(option);
    console.log("Inside handleButtonClick:", option);
  
    let welcomeMessage = "";
  
    // Set the welcome message based on the selected mode
    switch (option) {
      case "location":
        welcomeMessage =
        "Welcome to Location Recommendation Mode! Mention any of these keywords, and I'll find the nearest options for you:\n" +
        "\t- restaurant\n" +
        "\t- mosque\n" +
        "\t- spa\n" +
        "\t- museum\n" +
        "\t- park\n" +
        "\t- beach\n" +
        "\t- shopping\n" +
        "\t- art\n" +
        "\t- zoo\n" +
        "\t- aquarium\n" +
        "\t- historical\n" +
        "\t- theater\n" +
        "\t- coffee\n" +
        "Just let me know what you're looking for, and I'll handle the rest!";
      break;
      case "mood":
        welcomeMessage =
          "Welcome to Mood Recommendation Mode! Let me know how you're feeling, and I'll suggest something to match your mood.";
        break;
      case "planner":
        welcomeMessage =
          "Hi! Would you like to create an Itinerary Planner? let me help you with the planning!";
        break;
      default:
        welcomeMessage = "Welcome to Holly Chatbot! How can I assist you today?";
        break;
    }
  
    // Format the current date as a timestamp
    const timestamp = new Date().toLocaleDateString("en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }); // Formats to date only (e.g., 01/07/2025)
  
    // Add the welcome message to the chatbot messages
    setMessages((prevMessages) => [
      ...prevMessages,
      { text: welcomeMessage, sender: "bot", timestamp },
    ]);
  };
  


  const sendWelcomeMessage = () => {
    if (!welcomeMessageSent) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: "Welcome to Holly Tourism! How can I help you?", sender: "bot" },
        { text: "Please choose one of the options below:", sender: "bot" },
      ]);
      setWelcomeMessageSent(true);
    }
  };
  

  const fetchChatHistory = async () => {
    try {
      const history = await chatController.getChatHistory();
      console.log("Fetched chat history:", history); // Log the fetched data
  
      if (Array.isArray(history)) {
        setChatHistory(history);
      } else {
        throw new Error("Invalid chat history data");
      }
    } catch (error) {
      console.error("Error fetching chat history:", error);
      setChatHistory([]);
    }
  };

  const toggleSidebar = () => {
    if (isAuthenticated) {
      setShowSidebar((prev) => !prev); // Toggle sidebar only if logged in
    } else {
      alert("Please log in to access more functions.");
    }
  };
  

  useEffect(() => {
    if (showHistory) fetchChatHistory();
  }, [showHistory]);

  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [messages, chatHistory]);




  return (
    <div style={{ position: "fixed", bottom: "20px", right: "20px", zIndex: 1000 }}>
  {/* Chat Toggle Button */}
  <button
    onClick={() => {
      toggleChat();
      sendWelcomeMessage();
      fetchFAQs();
    }}
    style={{
      backgroundColor: "#007BFF",
      color: "#fff",
      border: "none",
      borderRadius: "50%",
      width: "60px",
      height: "60px",
      fontSize: "24px",
      cursor: "pointer",
      boxShadow: "0 6px 12px rgba(0, 0, 0, 0.3)",
    }}
    aria-label="Chat"
  >
    💬
  </button>

  {/* Chat Window */}
  {isOpen && (
    <div
      style={{
        position: "absolute",
        bottom: "90px",
        right: "0",
        width: "600px",
        height: "700px",
        background: "#fff",
        border: "1px solid #ddd",
        borderRadius: "8px",
        boxShadow: "0 6px 12px rgba(0, 0, 0, 0.2)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Chat Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "10px",
          background: 'linear-gradient(to right,rgb(10, 68, 228), #87CEFA)', // Dark blue to light blue
          color: "#fff",
          borderTopLeftRadius: "8px",
          borderTopRightRadius: "8px",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.2)",
        }}
      >
        <strong style={{ fontSize: "18px", fontWeight: "600" }}>Holly</strong>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {isAuthenticated && (
            <button
              onClick={() => setShowHistory(!showHistory)}
              style={{
                background: showHistory
                  ? "linear-gradient(to right, #ff512f, #fed766)"
                  : "linear-gradient(to right, #4facfe, #009fb7)",
                color: "#fff",
                border: "none",
                padding: "8px 20px",
                borderRadius: "20px",
                fontWeight: "500",
                cursor: "pointer",
              }}
            >
              {showHistory ? "Close History" : "View History"}
            </button>
          )}
          <button
            onClick={toggleChat}
            style={{
              backgroundColor: "transparent",
              color: "#fff",
              border: "none",
              fontSize: "18px",
              cursor: "pointer",
            }}
            aria-label="Close Chat"
          >
            ✖
          </button>
        </div>
      </div>


      {/* Chat Body */}
        <div
          ref={chatBodyRef}
          style={{
            flex: "1",
            padding: "10px",
            overflowY: "auto",
            background: "#E6E6EA",
            color: "#fff",
            display: "flex",
            flexDirection: "column",
          }}
          className="chat-body"
        >
          {/* Title for FAQ Section */}
          <h2
            style={{
              textAlign: "center",
              fontSize: "20px",
              fontWeight: "bold",
              marginBottom: "15px",
              color: "#333",
            }}
          >
            Frequently Asked Questions (FAQs)
          </h2>

          {/* Render FAQs */}
          {faqContent && faqContent.length > 0 ? (
            faqContent.map((faq, index) => (
              <div
                key={index}
                style={{
                  border: "1px solid #ccc",
                  marginBottom: "10px",
                  padding: "10px",
                  borderRadius: "8px",
                  cursor: "pointer",
                  background: expandedIndex === index ? "#f0f8ff" : "white",
                  boxShadow: "0 2px 5px rgba(0, 0, 0, 0.2)",
                }}
                onClick={() => toggleExpandFAQ(index)}
              >
                <div
                  style={{
                    fontWeight: "bold",
                    color: "#333",
                    fontSize: "16px",
                  }}
                >
                  {faq.ques}
                </div>
                {expandedIndex === index && (
                  <div
                    style={{
                      marginTop: "10px",
                      color: "#555",
                      lineHeight: "1.5",
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    <ReactMarkdown
                      components={{
                        a: ({ href, children }) => (
                          <a
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              color: "#007BFF",
                              textDecoration: "underline",
                            }}
                          >
                            {children}
                          </a>
                        ),
                        strong: ({ children }) => (
                          <strong
                            style={{
                              color: "#000",
                              fontWeight: "bold",
                            }}
                          >
                            {children}
                          </strong>
                        ),
                        ul: ({ children }) => (
                          <ul style={{ paddingLeft: "20px", marginTop: "10px" }}>
                            {children}
                          </ul>
                        ),
                        li: ({ children }) => (
                          <li
                            style={{
                              marginBottom: "5px",
                              lineHeight: "1.5",
                            }}
                          >
                            {children}
                          </li>
                        ),
                      }}
                    >
                      {faq.answer}
                    </ReactMarkdown>
                  </div>
                )}
              </div>
            ))
          ) : (
            <p style={{ color: "#333", textAlign: "center" }}>
              Loading FAQs...
            </p>
          )}
            
            {/* Chat Messages */}
            {(showHistory ? [...chatHistory].reverse() : messages).map((message, index) => {
              // Debug log to track rendering and message state

              return (
                
                <div
                  key={index}
                  style={{
                    display: "flex",
                    flexDirection: message.sender === "user" ? "row" : "row-reverse",
                    alignItems: "flex-start",
                    marginBottom: "10px",
                  }}
                >

                  <div
                    style={{
                      padding: "12px",
                      background: message.sender === "user" ? "rgb(89, 119, 158)" : "#455A64",
                      color: message.sender === "user" ? "#000" : "#fff",
                      borderRadius: "12px",
                      maxWidth: "85%",
                      textAlign: "left",
                      wordBreak: "break-word",
                      boxShadow: "0 3px 6px rgba(0, 0, 0, 0.1)",
                    }}
                  >
                    {/* Render user messages */}
                    {message.sender === "user" && (
                      <>
                        <p>{message.text}</p>
                      </>
                    )}

                    {/* Render bot messages with Markdown */}
                    {message.sender === "bot" && message.text && (
                      <>
                        <ReactMarkdown
                          components={{
                            a: ({ href, children }) => (
                              <a
                                href={href}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                  color: "#007BFF",
                                  textDecoration: "underline",
                                }}
                              >
                                {children}
                              </a>
                            ),
                          }}
                        >
                          {message.text.replace(/\n/g, "  \n")}
                        </ReactMarkdown>
                      </>
                    
                    )}

                      {message.richContent && (
                        <div style={{ marginTop: "10px" }}>
                          {message.richContent
                            .filter((content): content is JSX.Element => React.isValidElement(content))
                            .map((content, i) => (
                              <div key={i} style={{ marginBottom: "10px" }}>
                                {content}
                              </div>
                            ))}
                        </div>
                      )}

                      {/* Render map-specific messages */}
                      {message.text && message.text.includes("https://www.google.com/maps/embed/v1/directions") && (
                        <iframe
                          src={message.text}
                          width="100%"
                          height="300"
                          style={{
                            border: "none",
                            borderRadius: "8px",
                          }}
                          allowFullScreen
                          loading="lazy"
                        ></iframe>
                      )}

                      
                  </div>
                  
                </div>
              );
            })}
        </div>
     
            {/* Typing Indicator Below the Chat Body */}
            {isTyping && (
              <div
                style={{
                  padding: "10px",
                  background: "#E6E6EA",
                  textAlign: "right",
                  fontSize: "12px", // Smaller text
                  color: "black", // Black text
                  fontStyle: "italic",
                }}
              >
                Typing...
              </div>
            )}

    <button
        onClick={() => toggleSidebar()} // Toggles the sidebar
        style={{
          backgroundColor: "#FE4A49",
          background: 'linear-gradient(to right,rgb(33, 33, 240), #87CEFA)', // Dark blue to light blue
          border: "none",
          padding: "12px",
          width: "100%",
          cursor: "pointer",
          borderRadius: "4px",
          fontWeight: "bold", // Optional: improve text readability
          boxShadow: "0px 2px 5px rgba(0, 0, 0, 0.2)", // Optional: add a slight shadow
          transition: "background 0.3s ease", // Optional: smooth hover effect
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.backgroundColor = "#FF6A6B"; // Explicitly cast to HTMLElement
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.backgroundColor = "#FE4A49"; // Explicitly cast to HTMLElement
        }}
      >
        More Functions
</button>




{/* Sidebar */}
{showSidebar && isAuthenticated &&(
    <div
    style={{
      position: "absolute",
      top: "58px",
      left: "-250px", // Adjust left position for thinner sidebar
      height: "40%", // Match the chatbot height
      background: 'linear-gradient(to right,rgb(41, 41, 233), #87CEFA)', // Dark blue to light blue
      zIndex: 2000,
      display: "flex",
      flexDirection: "column",
      padding: "3px 3px", // Reduce padding to match thinner width
      color: "#ffffff", // Changed to correct color code (white should be #ffffff)
      width: "250px", // Reduce sidebar width
      transition: "all 0.5s ease",
      outline: "2px solid #c1cad6", // Added outline here
    }}
    
    >
      {/* Close Button */}
      <button
        onClick={() => setShowSidebar(false)} // Closes the sidebar
        style={{
          background: "transparent",
          color: "#000",
          border: "none",
          fontSize: "15px",
          cursor: "pointer",
          alignSelf: "flex-end",
          marginBottom: "20px",
        }}
        aria-label="Close Sidebar"
      >
        ✖
      </button>

      {/* Sidebar Options */}
      <button
        onClick={() => handleButtonClick("basic")}
        style={{
          background: "#fff",
          color: "#000",
          border: "none",
          padding: "8px 10px",
          width: "100%",
          fontSize: "15px",
          marginBottom: "10px",
          cursor: "pointer",
          borderRadius: "6px",
          fontWeight: "bold",
          textAlign: "center",
        }}
      >
        Basic Mode
      </button>
      <button
        onClick={() => handleButtonClick("location")}
        style={{
          background: "#fff",
          color: "#000",
          border: "none",
          padding: "8px 10px",
          fontSize: "15px",
          width: "100%",
          marginBottom: "10px",
          cursor: "pointer",
          borderRadius: "6px",
          fontWeight: "bold",
          textAlign: "center",
        }}
      >
        Location Recommendation
      </button>
      <button
        onClick={() => handleButtonClick("mood")}
        style={{
          background: "#fff",
          color: "#000",
          border: "none",
          padding: "8px 10px",
          fontSize: "15px",
          width: "100%",
          marginBottom: "10px",
          cursor: "pointer",
          borderRadius: "6px",
          fontWeight: "bold",
          textAlign: "center",
        }}
      >
        Mood Recommendation
      </button>
      <button
        onClick={() => handleButtonClick("planner")}
        style={{
          background: "#fff",
          color: "#000",
          border: "none",
          padding: "8px 10px",
          fontSize: "15px",
          width: "100%",
          cursor: "pointer",
          borderRadius: "6px",
          fontWeight: "bold",
          textAlign: "center",
        }}
      >
        Planner
      </button>
    </div>
)}



          

          {/* Chat Footer */}

          <div
            style={{
              display: "flex",
              alignItems: "center",
              padding: "10px",
              borderTop: "1px solid #ddd",
              backgroundColor: "#fff",
            }}
          >
          
            <input
              type="text"
              placeholder="Type a message..."
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  sendMessage();
                }
              }}
              style={{
                flex: "1",
                padding: "10px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                outline: "none",
              }}
            />  
           
            <button
              onClick={sendMessage}
              style={{
                marginLeft: "10px",
                padding: "10px 16px",
                background: 'linear-gradient(to right,rgb(79, 102, 233), #87CEFA)', // Dark blue to light blue
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
              
            >
            
              Send
            </button>
            
          </div>
        </div>
      )}
    
        {mapVisible && mapCoordinates && (
          <MapComponent
            lat1={mapCoordinates.lat1}
            lng1={mapCoordinates.lng1}
            lat2={mapCoordinates.lat2}
            lng2={mapCoordinates.lng2}
            onClose={closeMap}
          />
      )}
    </div>
  )}

export default Chat;


