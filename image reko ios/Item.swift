//
//  Item.swift
//  image reko ios
//
//  Created by Maanas Krishna on 14/12/25.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
