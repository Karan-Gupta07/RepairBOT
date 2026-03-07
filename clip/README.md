# RepairBOT App Clip — Reactiv ClipKit Lab Submission

An iOS App Clip that lets users photograph broken items and instantly receive AI-powered repair analysis, including repairability score, step-by-step instructions, cost estimates, and links to parts and tools.

## Project Structure

```
clip/
├── README.md
└── RepairBOTClip/
    ├── RepairBOTClipApp.swift       # App entry point, App Clip URL handling
    ├── ContentView.swift            # Navigation state machine
    ├── CameraView.swift             # Camera capture + photo picker
    ├── AnalysisView.swift           # Loading spinner + results display
    ├── Models/
    │   └── RepairResult.swift       # Codable data model
    ├── Services/
    │   ├── APIService.swift         # Network layer (POST /analyze)
    │   └── MockData.swift           # Demo fallback data
    └── Assets.xcassets/
        └── Contents.json
```

## Requirements

- Xcode 15+
- iOS 16+ deployment target
- Swift 5.9+
- No external dependencies (pure Swift / SwiftUI)

## Setup

1. **Open in Xcode**
   - Open Xcode → File → New → Project → App (or App Clip)
   - Set product name to `RepairBOTClip`
   - Set bundle identifier to `com.repairbot.clip`
   - Copy the Swift files from `RepairBOTClip/` into your Xcode project

2. **Configure the API URL**
   - Open `Services/APIService.swift`
   - Change `baseURL` to point to your RepairBOT backend:
     ```swift
     static var baseURL = "http://localhost:8000"  // local dev
     // static var baseURL = "https://your-server.com"  // production
     ```

3. **App Clip Configuration** (if building as an actual App Clip target)
   - Add an App Clip target in Xcode (File → New → Target → App Clip)
   - Register the invocation URL `https://repairbot.app/repair` in the Associated Domains entitlement
   - Add `appclips:repairbot.app` to your Associated Domains

4. **Run in Simulator**
   - Select an iPhone simulator (iPhone 15 Pro recommended)
   - Press ⌘R to build and run
   - The camera option requires a physical device; use "Choose from Library" in the simulator

## Demo Mode

When the RepairBOT API is unreachable (network error, server down, etc.), the app automatically falls back to **demo mode** with realistic sample data. A yellow banner at the top of the results screen indicates that mock data is being displayed.

This is useful for:
- Hackathon demos without a running backend
- Testing the UI in the iOS Simulator
- Offline presentations

## App Clip Invocation

The App Clip is designed to be invoked via the URL:

```
https://repairbot.app/repair
```

This can be triggered from:
- Safari Smart App Banner
- NFC tag
- QR code
- Messages link

## Color Palette

The UI uses a dark theme matching the RepairBOT web app:

| Token       | Hex       |
|-------------|-----------|
| Background  | `#1a1814` |
| Card        | `#242019` |
| Elevated    | `#2e2922` |
| Border      | `#3d3630` |
| Muted text  | `#8c857c` |
| Primary text| `#f5f0e8` |
| Soft text   | `#b8b0a4` |
| Accent      | `#d4a03a` |
| High/green  | `#4ade80` |
| Medium/yellow| `#facc15`|
| Low/red     | `#f87171` |
