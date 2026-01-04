# Swift App Development Guide - DailyBrief

Complete guide for building the iOS app that integrates with the DailyBrief API.

---

## Table of Contents
1. [Project Setup](#project-setup)
2. [API Configuration](#api-configuration)
3. [Complete Swift Code](#complete-swift-code)
4. [UI Structure](#ui-structure)
5. [Authentication Flow](#authentication-flow)
6. [Data Fetching](#data-fetching)
7. [Error Handling](#error-handling)
8. [Local Storage & Caching](#local-storage--caching)
9. [Testing](#testing)
10. [Deployment Checklist](#deployment-checklist)

---

## Project Setup

### 1. Create New Xcode Project
```
File → New → Project
Choose: iOS → App
Product Name: DailyBrief
Interface: SwiftUI
Language: Swift
```

### 2. Required Capabilities
- **Keychain Sharing**: For secure token storage
- **Background Fetch**: For periodic data refresh
- **Push Notifications**: (Optional) For reminders

### 3. Minimum Requirements
- iOS 15.0+
- Swift 5.5+
- SwiftUI

---

## API Configuration

### Base Configuration
```swift
struct APIConfig {
    static let baseURL = "https://your-api-domain.com"  // Change for production
    static let apiKey = "your_api_key_here"  // Get from backend team
    
    // For development
    #if DEBUG
    static let baseURL = "http://localhost:5001"
    #endif
}
```

### API Endpoints
- **Authentication**: `POST /api/users/authenticate`
- **Daily Brief**: `GET /api/v2/daily-brief`
- **Weather**: `GET /api/v2/weather`
- **Countdowns**: `GET /api/v2/countdowns`
- **Nameday**: `GET /api/v2/nameday`

---

## Complete Swift Code

### 1. Data Models

```swift
// MARK: - API Response Models

struct APIResponse<T: Codable>: Codable {
    let success: Bool
    let data: T?
    let error: String?
}

// MARK: - Authentication

struct AuthenticationRequest: Codable {
    let email: String
    let password: String
}

struct AuthenticationResponse: Codable {
    let success: Bool
    let user: User
    let token: String
    let tokenType: String
    let expiresIn: Int
    
    enum CodingKeys: String, CodingKey {
        case success, user, token
        case tokenType = "token_type"
        case expiresIn = "expires_in"
    }
}

// MARK: - User

struct User: Codable, Identifiable {
    let email: String
    let username: String
    let nickname: String?
    let timezone: String
    let language: String
    let personality: String
    
    var id: String { email }
}

// MARK: - Daily Brief

struct DailyBrief: Codable {
    let user: User
    let modulesEnabled: ModulesEnabled
    let weather: Weather?
    let countdowns: [Countdown]?
    let nameday: Nameday?
    let reminders: [Reminder]?
    let generatedAt: String
    
    enum CodingKeys: String, CodingKey {
        case user, weather, countdowns, nameday, reminders
        case modulesEnabled = "modules_enabled"
        case generatedAt = "generated_at"
    }
}

struct ModulesEnabled: Codable {
    let weather: Bool
    let countdown: Bool
    let reminder: Bool
}

// MARK: - Weather

struct Weather: Codable {
    let location: String
    let coordinates: Coordinates
    let timezone: String
    let today: DayWeather
    let weekForecast: [DayWeather]
    let summaryText: String
    
    enum CodingKeys: String, CodingKey {
        case location, coordinates, timezone, today
        case weekForecast = "week_forecast"
        case summaryText = "summary_text"
    }
}

struct Coordinates: Codable {
    let lat: Double
    let lon: Double
}

struct DayWeather: Codable, Identifiable {
    let date: String?
    let dayName: String?
    let tempMax: Double
    let tempMin: Double
    let precipitationSum: Double
    let precipitationProbability: Int
    let windSpeedMax: Double
    let condition: String
    
    var id: String {
        date ?? UUID().uuidString
    }
    
    enum CodingKeys: String, CodingKey {
        case date, condition
        case dayName = "day_name"
        case tempMax = "temp_max"
        case tempMin = "temp_min"
        case precipitationSum = "precipitation_sum"
        case precipitationProbability = "precipitation_probability"
        case windSpeedMax = "wind_speed_max"
    }
}

// MARK: - Countdown

struct Countdown: Codable, Identifiable {
    let name: String
    let date: String
    let yearly: Bool
    let daysLeft: Int
    let nextOccurrence: String
    let isPast: Bool
    let message: String
    
    var id: String {
        name + date
    }
    
    enum CodingKeys: String, CodingKey {
        case name, date, yearly, message
        case daysLeft = "days_left"
        case nextOccurrence = "next_occurrence"
        case isPast = "is_past"
    }
}

// MARK: - Nameday

struct Nameday: Codable {
    let date: String
    let dayName: String
    let names: String
    let message: String
    let language: String
    
    enum CodingKeys: String, CodingKey {
        case date, names, message, language
        case dayName = "day_name"
    }
}

// MARK: - Reminder (Placeholder)

struct Reminder: Codable {
    // To be implemented when backend adds reminder support
}

// MARK: - Weather Condition Extension

extension String {
    var weatherEmoji: String {
        switch self {
        case "sunny", "sunny_hot": return "☀️"
        case "cloudy": return "☁️"
        case "rainy", "raining": return "🌧️"
        case "heavy_rain": return "⛈️"
        case "thunderstorm": return "⚡"
        case "snowing": return "❄️"
        case "foggy": return "🌫️"
        case "windy": return "💨"
        case "hot", "heatwave": return "🔥"
        case "cold", "freezing", "blizzard": return "🥶"
        case "mild": return "😊"
        default: return "🌤️"
        }
    }
}
```

### 2. Keychain Helper

```swift
import Foundation
import Security

class KeychainHelper {
    static let shared = KeychainHelper()
    private init() {}
    
    private let service = "com.yourapp.dailybrief"
    
    func save(_ value: String, for key: String) {
        let data = Data(value.utf8)
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        
        // Delete any existing item
        SecItemDelete(query as CFDictionary)
        
        // Add new item
        SecItemAdd(query as CFDictionary, nil)
    }
    
    func get(_ key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]
        
        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)
        
        guard let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }
    
    func delete(_ key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key
        ]
        
        SecItemDelete(query as CFDictionary)
    }
}
```

### 3. API Service

```swift
import Foundation

enum APIError: Error, LocalizedError {
    case invalidURL
    case networkError(Error)
    case invalidResponse
    case decodingError(Error)
    case unauthorized
    case serverError(String)
    case rateLimitExceeded
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .invalidResponse:
            return "Invalid server response"
        case .decodingError(let error):
            return "Failed to parse data: \(error.localizedDescription)"
        case .unauthorized:
            return "Please login again"
        case .serverError(let message):
            return message
        case .rateLimitExceeded:
            return "Too many requests. Please try again later."
        }
    }
}

class APIService: ObservableObject {
    static let shared = APIService()
    
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    
    private var jwtToken: String? {
        didSet {
            isAuthenticated = jwtToken != nil
            if let token = jwtToken {
                KeychainHelper.shared.save(token, for: "jwt_token")
            } else {
                KeychainHelper.shared.delete("jwt_token")
            }
        }
    }
    
    private init() {
        // Load token from keychain on init
        jwtToken = KeychainHelper.shared.get("jwt_token")
        isAuthenticated = jwtToken != nil
    }
    
    // MARK: - Authentication
    
    func login(email: String, password: String) async throws -> User {
        guard let url = URL(string: "\(APIConfig.baseURL)/api/users/authenticate") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue(APIConfig.apiKey, forHTTPHeaderField: "X-API-Key")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = AuthenticationRequest(email: email, password: password)
        request.httpBody = try JSONEncoder().encode(body)
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.invalidResponse
            }
            
            if httpResponse.statusCode == 401 {
                throw APIError.unauthorized
            }
            
            if httpResponse.statusCode == 429 {
                throw APIError.rateLimitExceeded
            }
            
            let authResponse = try JSONDecoder().decode(AuthenticationResponse.self, from: data)
            
            if authResponse.success {
                jwtToken = authResponse.token
                currentUser = authResponse.user
                return authResponse.user
            } else {
                throw APIError.serverError("Authentication failed")
            }
        } catch let error as APIError {
            throw error
        } catch {
            throw APIError.networkError(error)
        }
    }
    
    func logout() {
        jwtToken = nil
        currentUser = nil
    }
    
    // MARK: - Data Fetching
    
    func getDailyBrief() async throws -> DailyBrief {
        guard let token = jwtToken else {
            throw APIError.unauthorized
        }
        
        guard let url = URL(string: "\(APIConfig.baseURL)/api/v2/daily-brief") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.invalidResponse
            }
            
            if httpResponse.statusCode == 401 {
                logout()
                throw APIError.unauthorized
            }
            
            if httpResponse.statusCode == 429 {
                throw APIError.rateLimitExceeded
            }
            
            let apiResponse = try JSONDecoder().decode(APIResponse<DailyBrief>.self, from: data)
            
            if apiResponse.success, let brief = apiResponse.data {
                return brief
            } else {
                throw APIError.serverError(apiResponse.error ?? "Unknown error")
            }
        } catch let error as APIError {
            throw error
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }
    
    func getWeather() async throws -> Weather {
        guard let token = jwtToken else {
            throw APIError.unauthorized
        }
        
        guard let url = URL(string: "\(APIConfig.baseURL)/api/v2/weather") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode == 401 {
            logout()
            throw APIError.unauthorized
        }
        
        let apiResponse = try JSONDecoder().decode(APIResponse<Weather>.self, from: data)
        
        if apiResponse.success, let weather = apiResponse.data {
            return weather
        } else {
            throw APIError.serverError(apiResponse.error ?? "Failed to fetch weather")
        }
    }
    
    func getCountdowns() async throws -> [Countdown] {
        guard let token = jwtToken else {
            throw APIError.unauthorized
        }
        
        guard let url = URL(string: "\(APIConfig.baseURL)/api/v2/countdowns") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode == 401 {
            logout()
            throw APIError.unauthorized
        }
        
        let apiResponse = try JSONDecoder().decode(APIResponse<[Countdown]>.self, from: data)
        
        if apiResponse.success, let countdowns = apiResponse.data {
            return countdowns
        } else {
            throw APIError.serverError(apiResponse.error ?? "Failed to fetch countdowns")
        }
    }
    
    func getNameday() async throws -> Nameday? {
        guard let token = jwtToken else {
            throw APIError.unauthorized
        }
        
        guard let url = URL(string: "\(APIConfig.baseURL)/api/v2/nameday") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode == 401 {
            logout()
            throw APIError.unauthorized
        }
        
        let apiResponse = try JSONDecoder().decode(APIResponse<Nameday?>.self, from: data)
        
        return apiResponse.data
    }
}
```

### 4. View Models

```swift
import Foundation

@MainActor
class DailyBriefViewModel: ObservableObject {
    @Published var dailyBrief: DailyBrief?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = APIService.shared
    
    func fetchDailyBrief() async {
        isLoading = true
        errorMessage = nil
        
        do {
            dailyBrief = try await apiService.getDailyBrief()
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
}

@MainActor
class WeatherViewModel: ObservableObject {
    @Published var weather: Weather?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = APIService.shared
    
    func fetchWeather() async {
        isLoading = true
        errorMessage = nil
        
        do {
            weather = try await apiService.getWeather()
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
}

@MainActor
class CountdownViewModel: ObservableObject {
    @Published var countdowns: [Countdown] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = APIService.shared
    
    func fetchCountdowns() async {
        isLoading = true
        errorMessage = nil
        
        do {
            countdowns = try await apiService.getCountdowns()
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
}
```

---

## UI Structure

### 1. App Entry Point

```swift
import SwiftUI

@main
struct DailyBriefApp: App {
    @StateObject private var apiService = APIService.shared
    
    var body: some Scene {
        WindowGroup {
            if apiService.isAuthenticated {
                MainTabView()
                    .environmentObject(apiService)
            } else {
                LoginView()
                    .environmentObject(apiService)
            }
        }
    }
}
```

### 2. Login View

```swift
import SwiftUI

struct LoginView: View {
    @EnvironmentObject var apiService: APIService
    
    @State private var email = ""
    @State private var password = ""
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Image(systemName: "sun.max.fill")
                    .font(.system(size: 80))
                    .foregroundColor(.orange)
                
                Text("DailyBrief")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                VStack(spacing: 15) {
                    TextField("Email", text: $email)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .textContentType(.emailAddress)
                        .autocapitalization(.none)
                    
                    SecureField("Password", text: $password)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .textContentType(.password)
                }
                .padding(.horizontal)
                
                if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                        .multilineTextAlignment(.center)
                }
                
                Button(action: login) {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Text("Login")
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
                .padding(.horizontal)
                .disabled(isLoading || email.isEmpty || password.isEmpty)
                
                Spacer()
            }
            .padding()
            .navigationTitle("")
        }
    }
    
    private func login() {
        Task {
            isLoading = true
            errorMessage = nil
            
            do {
                _ = try await apiService.login(email: email, password: password)
            } catch {
                errorMessage = error.localizedDescription
            }
            
            isLoading = false
        }
    }
}
```

### 3. Main Tab View

```swift
import SwiftUI

struct MainTabView: View {
    var body: some View {
        TabView {
            DailyBriefView()
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
            
            WeatherView()
                .tabItem {
                    Label("Weather", systemImage: "cloud.sun.fill")
                }
            
            CountdownView()
                .tabItem {
                    Label("Events", systemImage: "calendar")
                }
            
            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
        }
    }
}
```

### 4. Daily Brief View

```swift
import SwiftUI

struct DailyBriefView: View {
    @StateObject private var viewModel = DailyBriefViewModel()
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    if viewModel.isLoading {
                        ProgressView("Loading your daily brief...")
                    } else if let error = viewModel.errorMessage {
                        ErrorView(message: error) {
                            Task {
                                await viewModel.fetchDailyBrief()
                            }
                        }
                    } else if let brief = viewModel.dailyBrief {
                        // User Info
                        UserInfoCard(user: brief.user)
                        
                        // Weather
                        if let weather = brief.weather {
                            WeatherCard(weather: weather)
                        }
                        
                        // Countdowns
                        if let countdowns = brief.countdowns, !countdowns.isEmpty {
                            CountdownsCard(countdowns: countdowns)
                        }
                        
                        // Nameday
                        if let nameday = brief.nameday {
                            NamedayCard(nameday: nameday)
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Daily Brief")
            .refreshable {
                await viewModel.fetchDailyBrief()
            }
        }
        .task {
            await viewModel.fetchDailyBrief()
        }
    }
}

// MARK: - Card Views

struct UserInfoCard: View {
    let user: User
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Hello, \(user.nickname ?? user.username)! 👋")
                .font(.title2)
                .fontWeight(.bold)
            
            HStack {
                Image(systemName: "clock")
                Text(user.timezone)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }
}

struct WeatherCard: View {
    let weather: Weather
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "location.fill")
                Text(weather.location)
                    .font(.headline)
                Spacer()
                Text(weather.today.condition.weatherEmoji)
                    .font(.title)
            }
            
            HStack(spacing: 30) {
                VStack {
                    Text("\(Int(weather.today.tempMax))°")
                        .font(.title)
                        .fontWeight(.bold)
                    Text("High")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                VStack {
                    Text("\(Int(weather.today.tempMin))°")
                        .font(.title)
                        .fontWeight(.semibold)
                    Text("Low")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                VStack {
                    Text("\(weather.today.precipitationProbability)%")
                        .font(.title)
                        .fontWeight(.semibold)
                    Text("Rain")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            if !weather.weekForecast.isEmpty {
                Divider()
                
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 15) {
                        ForEach(weather.weekForecast) { day in
                            WeekDayView(day: day)
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }
}

struct WeekDayView: View {
    let day: DayWeather
    
    var body: some View {
        VStack(spacing: 8) {
            Text(day.dayName ?? "")
                .font(.caption)
                .fontWeight(.medium)
            
            Text(day.condition.weatherEmoji)
                .font(.title2)
            
            Text("\(Int(day.tempMax))°")
                .fontWeight(.bold)
            
            Text("\(Int(day.tempMin))°")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(width: 60)
    }
}

struct CountdownsCard: View {
    let countdowns: [Countdown]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Upcoming Events")
                .font(.headline)
            
            ForEach(countdowns) { countdown in
                HStack {
                    VStack(alignment: .leading) {
                        Text(countdown.name)
                            .font(.subheadline)
                            .fontWeight(.medium)
                        Text(countdown.message)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    Spacer()
                    Text("\(countdown.daysLeft)")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.blue)
                }
                .padding(.vertical, 4)
                
                if countdown.id != countdowns.last?.id {
                    Divider()
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }
}

struct NamedayCard: View {
    let nameday: Nameday
    
    var body: some View {
        HStack {
            Image(systemName: "gift.fill")
                .font(.title2)
                .foregroundColor(.purple)
            
            VStack(alignment: .leading) {
                Text("Name Day")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text(nameday.names)
                    .font(.headline)
            }
            
            Spacer()
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(15)
        .shadow(radius: 2)
    }
}

struct ErrorView: View {
    let message: String
    let retry: () -> Void
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 50))
                .foregroundColor(.orange)
            
            Text(message)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
            
            Button("Retry", action: retry)
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
        }
        .padding()
    }
}
```

### 5. Weather View

```swift
import SwiftUI

struct WeatherView: View {
    @StateObject private var viewModel = WeatherViewModel()
    
    var body: some View {
        NavigationView {
            ScrollView {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.errorMessage {
                    ErrorView(message: error) {
                        Task { await viewModel.fetchWeather() }
                    }
                } else if let weather = viewModel.weather {
                    VStack(spacing: 20) {
                        WeatherCard(weather: weather)
                        
                        // Week Forecast Details
                        VStack(alignment: .leading, spacing: 15) {
                            Text("7-Day Forecast")
                                .font(.title2)
                                .fontWeight(.bold)
                            
                            ForEach(weather.weekForecast) { day in
                                WeekDayDetailView(day: day)
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("Weather")
            .refreshable {
                await viewModel.fetchWeather()
            }
        }
        .task {
            await viewModel.fetchWeather()
        }
    }
}

struct WeekDayDetailView: View {
    let day: DayWeather
    
    var body: some View {
        HStack {
            Text(day.dayName ?? "")
                .frame(width: 80, alignment: .leading)
            
            Text(day.condition.weatherEmoji)
                .font(.title3)
            
            Spacer()
            
            Text("\(day.precipitationProbability)%")
                .foregroundColor(.blue)
                .frame(width: 50)
            
            Text("\(Int(day.tempMax))°/\(Int(day.tempMin))°")
                .fontWeight(.semibold)
                .frame(width: 70, alignment: .trailing)
        }
        .padding(.vertical, 8)
    }
}
```

### 6. Countdown View

```swift
import SwiftUI

struct CountdownView: View {
    @StateObject private var viewModel = CountdownViewModel()
    
    var body: some View {
        NavigationView {
            Group {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.errorMessage {
                    ErrorView(message: error) {
                        Task { await viewModel.fetchCountdowns() }
                    }
                } else if viewModel.countdowns.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "calendar.badge.plus")
                            .font(.system(size: 60))
                            .foregroundColor(.secondary)
                        Text("No events yet")
                            .font(.headline)
                            .foregroundColor(.secondary)
                    }
                } else {
                    List(viewModel.countdowns) { countdown in
                        CountdownRow(countdown: countdown)
                    }
                }
            }
            .navigationTitle("Events")
            .refreshable {
                await viewModel.fetchCountdowns()
            }
        }
        .task {
            await viewModel.fetchCountdowns()
        }
    }
}

struct CountdownRow: View {
    let countdown: Countdown
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(countdown.name)
                    .font(.headline)
                
                Text(countdown.date)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                if countdown.yearly {
                    Label("Yearly", systemImage: "repeat")
                        .font(.caption2)
                        .foregroundColor(.blue)
                }
            }
            
            Spacer()
            
            VStack {
                Text("\(countdown.daysLeft)")
                    .font(.title)
                    .fontWeight(.bold)
                    .foregroundColor(countdown.isPast ? .gray : .blue)
                
                Text("days")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 8)
    }
}
```

### 7. Settings View

```swift
import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var apiService: APIService
    
    var body: some View {
        NavigationView {
            Form {
                if let user = apiService.currentUser {
                    Section("Account") {
                        HStack {
                            Text("Email")
                            Spacer()
                            Text(user.email)
                                .foregroundColor(.secondary)
                        }
                        
                        HStack {
                            Text("Username")
                            Spacer()
                            Text(user.username)
                                .foregroundColor(.secondary)
                        }
                        
                        HStack {
                            Text("Timezone")
                            Spacer()
                            Text(user.timezone)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                
                Section {
                    Button("Logout", role: .destructive) {
                        apiService.logout()
                    }
                }
            }
            .navigationTitle("Settings")
        }
    }
}
```

---

## Authentication Flow

### Token Management

```swift
// 1. Login
let user = try await apiService.login(email: email, password: password)
// Token is automatically saved to Keychain

// 2. Token is included in all subsequent requests
// Handled automatically by APIService

// 3. Token expires after 7 days
// User must login again

// 4. Handle token expiration
// If API returns 401, logout user automatically:
if httpResponse.statusCode == 401 {
    logout() // Clears token and shows login screen
    throw APIError.unauthorized
}
```

### Auto-Login on App Launch

```swift
@main
struct DailyBriefApp: App {
    @StateObject private var apiService = APIService.shared
    
    var body: some Scene {
        WindowGroup {
            // Token loaded from Keychain in APIService.init()
            if apiService.isAuthenticated {
                MainTabView()
            } else {
                LoginView()
            }
        }
    }
}
```

---

## Data Fetching

### Pull-to-Refresh

```swift
.refreshable {
    await viewModel.fetchDailyBrief()
}
```

### Automatic Loading

```swift
.task {
    await viewModel.fetchDailyBrief()
}
```

### Manual Refresh

```swift
Button("Refresh") {
    Task {
        await viewModel.fetchWeather()
    }
}
```

---

## Error Handling

### Display Errors

```swift
if let error = viewModel.errorMessage {
    Text(error)
        .foregroundColor(.red)
}
```

### Retry Logic

```swift
struct ErrorView: View {
    let message: String
    let retry: () -> Void
    
    var body: some View {
        VStack {
            Text(message)
            Button("Retry", action: retry)
        }
    }
}
```

### Handle Specific Errors

```swift
do {
    try await apiService.login(email: email, password: password)
} catch APIError.unauthorized {
    errorMessage = "Invalid email or password"
} catch APIError.rateLimitExceeded {
    errorMessage = "Too many attempts. Try again later."
} catch {
    errorMessage = error.localizedDescription
}
```

---

## Local Storage & Caching

### Cache Data with UserDefaults

```swift
class CacheManager {
    static let shared = CacheManager()
    
    func saveDailyBrief(_ brief: DailyBrief) {
        if let encoded = try? JSONEncoder().encode(brief) {
            UserDefaults.standard.set(encoded, forKey: "cached_daily_brief")
        }
    }
    
    func loadDailyBrief() -> DailyBrief? {
        guard let data = UserDefaults.standard.data(forKey: "cached_daily_brief"),
              let brief = try? JSONDecoder().decode(DailyBrief.self, from: data) else {
            return nil
        }
        return brief
    }
}
```

### Use Cache in ViewModel

```swift
func fetchDailyBrief() async {
    // Show cached data immediately
    dailyBrief = CacheManager.shared.loadDailyBrief()
    
    isLoading = true
    
    do {
        let fresh = try await apiService.getDailyBrief()
        dailyBrief = fresh
        CacheManager.shared.saveDailyBrief(fresh)
    } catch {
        // If fetch fails, keep showing cached data
        errorMessage = error.localizedDescription
    }
    
    isLoading = false
}
```

---

## Testing

### Test API Connection

```swift
// In a test file or playground
Task {
    do {
        let user = try await APIService.shared.login(
            email: "test@example.com",
            password: "testpassword"
        )
        print("✅ Login successful: \(user.email)")
        
        let brief = try await APIService.shared.getDailyBrief()
        print("✅ Daily brief fetched")
        print("Weather: \(brief.weather?.location ?? "none")")
        print("Countdowns: \(brief.countdowns?.count ?? 0)")
    } catch {
        print("❌ Error: \(error)")
    }
}
```

---

## Deployment Checklist

### Before Submitting to App Store

- [ ] Change `APIConfig.baseURL` to production URL
- [ ] Remove debug prints
- [ ] Test on multiple iOS versions (15.0+)
- [ ] Test on different screen sizes (iPhone SE, Pro Max)
- [ ] Add app icons (1024x1024 required)
- [ ] Add launch screen
- [ ] Test error scenarios (no internet, invalid token)
- [ ] Test rate limiting behavior
- [ ] Add privacy policy URL in App Store Connect
- [ ] Test token expiration (force 401 response)
- [ ] Implement background refresh (optional)
- [ ] Add analytics (optional)
- [ ] Test with real user accounts

### App Store Information

**Required:**
- App Name: DailyBrief
- Category: Weather or Productivity
- Privacy Policy: Link to your privacy policy
- Description: Write compelling description
- Screenshots: 6.5" iPhone (required), iPad (optional)
- Keywords: weather, daily, brief, countdown, events

### Version 1.0 Features

**Included:**
- ✅ User authentication
- ✅ Daily brief view
- ✅ Weather with 7-day forecast
- ✅ Countdown events
- ✅ Name days
- ✅ Pull-to-refresh
- ✅ Secure token storage

**Future Versions:**
- Push notifications
- Widget support
- Apple Watch companion
- Siri shortcuts
- Multiple locations
- Custom themes

---

## Quick Reference

### API Endpoints

| Endpoint | Method | Auth | Returns |
|----------|--------|------|---------|
| `/api/users/authenticate` | POST | API Key | JWT Token |
| `/api/v2/daily-brief` | GET | JWT | Complete user data |
| `/api/v2/weather` | GET | JWT | Weather + forecast |
| `/api/v2/countdowns` | GET | JWT | Countdown list |
| `/api/v2/nameday` | GET | JWT | Nameday info |

### Rate Limits

- **Authentication**: 20 requests/hour
- **Data endpoints**: 50 requests/hour combined
- **Token expiration**: 7 days

### Important URLs

- **API Documentation**: `API_DOCUMENTATION.md`
- **Backend Repository**: GitHub - FilipJohanes/WetherApp
- **Support Email**: [Your support email]

---

## Support & Contact

For backend API issues or questions:
- Check `API_DOCUMENTATION.md`
- Run test script: `python test_jwt_api.py`
- Contact backend team for API key

For Swift development questions:
- Reference this guide
- Check Apple's SwiftUI documentation
- Test with provided code examples

---

## Version History

**v1.0 (Current)**
- Initial release
- JWT authentication
- Daily brief, weather, countdowns, namedays
- SwiftUI interface
- Secure token storage

---

**Good luck with your Swift app development! 🚀**

All the code provided in this guide is ready to use. Simply:
1. Create new Xcode project
2. Copy the models and API service
3. Build the UI with provided SwiftUI views
4. Configure API key and base URL
5. Test and deploy!
