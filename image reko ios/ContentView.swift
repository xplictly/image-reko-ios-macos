//
//  ContentView.swift
//  image reko ios
//
//  Created by Maanas Krishna on 14/12/25.
//

import SwiftUI
import SwiftData
#if os(macOS)
import UniformTypeIdentifiers
#endif
#if os(iOS)
import PhotosUI
#endif

struct ContentView: View {
    @Environment(\.modelContext) private var modelContext
    @Query private var items: [Item]
    
    @State private var cardAppeared = false
    @State private var buttonAppeared = false
    
    @State private var selectedImage: Image?
    @State private var selectedImageData: Data?
    
    @State private var isSearching = false
    @State private var searchResult: String?
    
    #if os(iOS)
    @State private var showingPhotoPicker = false
    @State private var photoPickerItem: PhotosPickerItem?
    #elseif os(macOS)
    @State private var showingFileImporter = false
    #endif

    var body: some View {
        ZStack {
            // Glassy background with subtle blur
            Color.gray.opacity(0.15)
                .ignoresSafeArea()
                .background(.ultraThinMaterial)
                .ignoresSafeArea()
            
            VStack(spacing: 30) {
                // Center card
                VStack(spacing: 16) {
                    if let selectedImage {
                        selectedImage
                            .resizable()
                            .scaledToFit()
                            .frame(width: 120, height: 120)
                            .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                            .shadow(color: .accentColor.opacity(0.4), radius: 12, x: 0, y: 6)
                    } else {
                        Image(systemName: "magnifyingglass.circle.fill")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 80, height: 80)
                            .foregroundColor(.accentColor)
                            .shadow(color: .accentColor.opacity(0.4), radius: 12, x: 0, y: 6)
                    }
                    
                    Text("Reverse Image Search")
                        .font(.largeTitle.bold())
                        .foregroundColor(.primary)
                    
                    Text("Upload or capture an image to find similar ones on the web.")
                        .font(.body)
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)
                        .padding(.horizontal, 24)
                    
                    #if os(iOS)
                    Button {
                        showingPhotoPicker = true
                    } label: {
                        Label("Choose Image", systemImage: "plus.viewfinder")
                            .font(.title3.bold())
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.accentColor)
                            .foregroundColor(.white)
                            .clipShape(Capsule())
                            .shadow(color: Color.accentColor.opacity(0.5), radius: 10, x: 0, y: 5)
                    }
                    .padding(.horizontal, 24)
                    .scaleEffect(buttonAppeared ? 1 : 0.8)
                    .opacity(buttonAppeared ? 1 : 0)
                    .animation(.easeOut(duration: 0.5).delay(0.4), value: buttonAppeared)
                    .photosPicker(isPresented: $showingPhotoPicker, selection: $photoPickerItem, matching: .images)
                    .onChange(of: photoPickerItem) { newValue in
                        Task {
                            if let data = try? await newValue?.loadTransferable(type: Data.self) {
                                selectedImageData = data
                                if let uiImage = UIImage(data: data) {
                                    selectedImage = Image(uiImage: uiImage)
                                } else {
                                    selectedImage = nil
                                }
                            }
                        }
                    }
                    #elseif os(macOS)
                    Button {
                        showingFileImporter = true
                    } label: {
                        Label("Choose Image", systemImage: "plus.viewfinder")
                            .font(.title3.bold())
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.accentColor)
                            .foregroundColor(.white)
                            .clipShape(Capsule())
                            .shadow(color: Color.accentColor.opacity(0.5), radius: 10, x: 0, y: 5)
                    }
                    .padding(.horizontal, 24)
                    .scaleEffect(buttonAppeared ? 1 : 0.8)
                    .opacity(buttonAppeared ? 1 : 0)
                    .animation(.easeOut(duration: 0.5).delay(0.4), value: buttonAppeared)
                    .fileImporter(isPresented: $showingFileImporter, allowedContentTypes: [.image], allowsMultipleSelection: false) { result in
                        switch result {
                        case .success(let urls):
                            if let url = urls.first, let data = try? Data(contentsOf: url) {
                                selectedImageData = data
                                if let nsImage = NSImage(data: data) {
                                    selectedImage = Image(nsImage: nsImage)
                                } else {
                                    selectedImage = nil
                                }
                            }
                        case .failure:
                            break
                        }
                    }
                    #endif
                    
                    Button {
                        isSearching = true
                        searchResult = nil
                        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                            isSearching = false
                            searchResult = Bool.random() ? "Found visually similar images!" : "No matches found (simulated)"
                        }
                    } label: {
                        Text("Search")
                            .font(.title3.bold())
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(selectedImageData != nil ? Color.accentColor : Color.accentColor.opacity(0.4))
                            .foregroundColor(.white)
                            .clipShape(Capsule())
                            .shadow(color: (selectedImageData != nil ? Color.accentColor.opacity(0.5) : Color.accentColor.opacity(0.2)), radius: 10, x: 0, y: 5)
                    }
                    .padding(.horizontal, 24)
                    .disabled(selectedImageData == nil)
                    
                    if isSearching {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .accentColor))
                            .padding(.top, 8)
                    }
                    
                    if let result = searchResult {
                        Text(result)
                            .font(.body.weight(.semibold))
                            .foregroundColor(.primary)
                            .multilineTextAlignment(.center)
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(
                                RoundedRectangle(cornerRadius: 20, style: .continuous)
                                    .glassEffect(.regular, in: .rect(cornerRadius: 20))
                            )
                            .padding(.horizontal, 24)
                            .padding(.top, 8)
                    }
                }
                .padding(32)
                .background(.ultraThinMaterial)
                .clipShape(RoundedRectangle(cornerRadius: 30, style: .continuous))
                .shadow(color: Color.black.opacity(0.15), radius: 30, x: 0, y: 15)
                .scaleEffect(cardAppeared ? 1 : 0.8)
                .opacity(cardAppeared ? 1 : 0)
                .animation(.easeOut(duration: 0.6), value: cardAppeared)
                
                // Recent Searches section
                if !items.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Recent Searches")
                            .font(.title2.bold())
                            .padding(.horizontal, 24)
                            .padding(.top, 8)
                        
                        ScrollView {
                            VStack(spacing: 12) {
                                ForEach(items) { item in
                                    HStack {
                                        Image(systemName: "clock")
                                            .foregroundColor(.accentColor)
                                            .frame(width: 24)
                                        Text(item.timestamp, format: Date.FormatStyle(date: .numeric, time: .shortened))
                                            .foregroundColor(.primary)
                                        Spacer()
                                    }
                                    .padding()
                                    .background(
                                        RoundedRectangle(cornerRadius: 15, style: .continuous)
                                            .glassEffect(.regular, in: .rect(cornerRadius: 15))
                                            .shadow(color: Color.black.opacity(0.05), radius: 6, x: 0, y: 3)
                                    )
                                    .padding(.horizontal, 24)
                                }
                            }
                        }
                        .frame(maxHeight: 220)
                    }
                    .transition(.opacity.combined(with: .move(edge: .bottom)))
                    .animation(.easeInOut, value: items.count)
                }
                
                Spacer()
            }
            .padding(.top, 60)
        }
        .onAppear {
            cardAppeared = true
            buttonAppeared = true
        }
    }

    private func addItem() {
        withAnimation {
            let newItem = Item(timestamp: Date())
            modelContext.insert(newItem)
        }
    }

    private func deleteItems(offsets: IndexSet) {
        withAnimation {
            for index in offsets {
                modelContext.delete(items[index])
            }
        }
    }
}

#Preview {
    ContentView()
        .modelContainer(for: Item.self, inMemory: true)
}
