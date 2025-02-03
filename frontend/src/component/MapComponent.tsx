import React from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

const userIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
  iconSize: [25, 41], 
  iconAnchor: [12, 41], 
  popupAnchor: [1, -34], 
  shadowSize: [41, 41],
});

const destinationIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png", // Red marker icon
  iconRetinaUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png", // Retina red marker icon
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-shadow.png", 
  iconSize: [25, 41], // Default size
  iconAnchor: [12, 41], // Anchor point
  popupAnchor: [1, -34], // Popup position
  shadowSize: [41, 41], // Shadow size
});



interface MapComponentProps {
  lat1: number; // User's latitude
  lng1: number; // User's longitude
  lat2: number; // Destination latitude
  lng2: number; // Destination longitude
  onClose: () => void;
}

const MapComponent: React.FC<MapComponentProps> = ({ lat1, lng1, lat2, lng2, onClose }) => {
  const polylinePositions: [number, number][] = [
    [lat1, lng1],
    [lat2, lng2],
  ];

  return (
    <div
      style={{
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        width: "80%",
        height: "60%",
        backgroundColor: "#fff",
        zIndex: 1000,
        borderRadius: "8px",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
      }}
    >
      {/* Close Button */}
      <button
        onClick={onClose}
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          background: "red",
          color: "#fff",
          border: "none",
          padding: "10px",
          borderRadius: "4px",
          fontSize: "14px",
          cursor: "pointer",
          zIndex: 1100, // Ensures it is above the map
        }}
      >
        Close
      </button>

      {/* Leaflet Map */}
      <MapContainer
        center={[lat1, lng1]} // Center the map on the user's location
        zoom={13}
        style={{ height: "100%", borderRadius: "8px" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Marker for the user's location */}
        <Marker position={[lat1, lng1]} icon={userIcon}>
          <Popup>
            User's Location: {lat1}, {lng1}
          </Popup>
        </Marker>

        {/* Marker for the destination */}
        <Marker position={[lat2, lng2]} icon={destinationIcon}>
          <Popup>
            Destination: {lat2}, {lng2}
          </Popup>
        </Marker>

        {/* Polyline to draw the line between the two points */}
        <Polyline positions={polylinePositions} color="Green" />
      </MapContainer>
    </div>
  );
};

export default MapComponent;
