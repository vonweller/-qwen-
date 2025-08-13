"""
主窗口样式表
"""

MAIN_WINDOW_STYLE = """
QMainWindow {
    background-color: #F8F9FA;
}

#topBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4ECDC4, stop:1 #45B7B8);
    border-radius: 12px;
    color: white;
}

#timeLabel, #weatherLabel {
    color: white;
    font-size: 14px;
    font-weight: bold;
}

#settingsBtn {
    background-color: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 6px;
    color: white;
    padding: 6px 12px;
    font-size: 12px;
}

#settingsBtn:hover {
    background-color: rgba(255, 255, 255, 0.3);
}

#centralFrame {
    background-color: white;
    border-radius: 12px;
    border: 1px solid #E9ECEF;
}

#sidePanel {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E9ECEF;
}

#stepsFrame {
    background-color: #F8F9FA;
    border-radius: 8px;
    border: 1px solid #DEE2E6;
}

#stepIndicator {
    background-color: #E9ECEF;
    border-radius: 5px;
    color: #6C757D;
    font-size: 10px;
    font-weight: bold;
    border: 1px solid #CED4DA;
}

#stepIndicator[active="true"] {
    background-color: #4ECDC4;
    color: white;
    border: 1px solid #4ECDC4;
}

#infoCard {
    background-color: #F8F9FA;
    border-radius: 8px;
    border: 1px solid #DEE2E6;
}

#cardTitle {
    font-size: 12px;
    font-weight: bold;
    color: #2C3E50;
}

#cardContent {
    font-size: 11px;
    color: #6C757D;
}

#progressLabel {
    font-size: 11px;
    color: #6C757D;
    font-weight: bold;
}

#progressBar {
    border-radius: 6px;
    background-color: #E9ECEF;
}

#progressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4ECDC4, stop:1 #45B7B8);
    border-radius: 6px;
}

#bottomPanel {
    background-color: white;
    border-radius: 12px;
    border: 1px solid #E9ECEF;
}

#startBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #4ECDC4, stop:1 #45B7B8);
    border: none;
    border-radius: 25px;
    color: white;
    font-size: 14px;
    font-weight: bold;
}

#startBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #45B7B8, stop:1 #4ECDC4);
}

#startBtn:pressed {
    background-color: #3FBDB7;
}

#statusLabel {
    font-size: 16px;
    font-weight: bold;
    color: #2C3E50;
}

#recordsBtn {
    background-color: #6C757D;
    border: none;
    border-radius: 20px;
    color: white;
    font-size: 12px;
}

#recordsBtn:hover {
    background-color: #5A6268;
}

#mqttFrame {
    background-color: #F8F9FA;
    border-radius: 8px;
    border: 1px solid #DEE2E6;
}

#mqttTitle {
    font-size: 12px;
    font-weight: bold;
    color: #2C3E50;
}

#mqttMessage {
    font-size: 10px;
    color: #6C757D;
    background-color: #FFFFFF;
    border: 1px solid #E9ECEF;
    border-radius: 4px;
    padding: 4px;
}

#analysisFrame {
    background-color: #F8F9FA;
    border-radius: 8px;
    border: 1px solid #DEE2E6;
}

#analysisTitle {
    font-size: 12px;
    font-weight: bold;
    color: #2C3E50;
}

#analysisStatus {
    font-size: 11px;
    color: #6C757D;
    font-weight: bold;
}

#scoreLabel, #accuracyLabel {
    font-size: 10px;
    color: #495057;
    font-weight: bold;
    background-color: #E9ECEF;
    border-radius: 4px;
    padding: 2px 6px;
}

#feedbackLabel {
    font-size: 10px;
    color: #6C757D;
    background-color: #FFFFFF;
    border: 1px solid #E9ECEF;
    border-radius: 4px;
    padding: 4px;
}
"""