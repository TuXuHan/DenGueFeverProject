#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
from datetime import datetime, timedelta
import os

class DengueDataGenerator:
    def __init__(self):
        self.tainan_districts = [
            "中西區", "安平區", "東區", "南區", "北區", "安南區", "永康區", "歸仁區", "新化區", "左鎮區",
            "玉井區", "南化區", "楠西區", "善化區", "大內區", "山上區", "新市區", "安定區", "關廟區", "龍崎區",
            "仁德區", "七股區", "佳里區", "學甲區", "西港區", "將軍區", "北門區", "新營區", "鹽水區", "白河區",
            "後壁區", "東山區", "六甲區", "官田區", "麻豆區", "下營區", "柳營區"
        ]
        
        self.risk_levels = ["低風險", "中風險", "高風險", "極高風險"]
        
        self.population_base = {
            "中西區": 78000, "安平區": 65000, "東區": 185000, "南區": 125000, "北區": 135000,
            "安南區": 195000, "永康區": 235000, "歸仁區": 68000, "新化區": 45000, "左鎮區": 5000,
            "玉井區": 15000, "南化區": 9000, "楠西區": 11000, "善化區": 48000, "大內區": 10000,
            "山上區": 8000, "新市區": 36000, "安定區": 31000, "關廟區": 35000, "龍崎區": 4000,
            "仁德區": 75000, "七股區": 23000, "佳里區": 60000, "學甲區": 28000, "西港區": 25000,
            "將軍區": 20000, "北門區": 12000, "新營區": 78000, "鹽水區": 28000, "白河區": 30000,
            "後壁區": 25000, "東山區": 22000, "六甲區": 23000, "官田區": 22000, "麻豆區": 45000,
            "下營區": 25000, "柳營區": 22000
        }
    
    def generate_dengue_cases(self, district):
        """生成登革熱病例數"""
        base_population = self.population_base.get(district, 50000)
        
        if base_population > 100000:
            cases = random.randint(0, 50)
        elif base_population > 50000:
            cases = random.randint(0, 30)
        else:
            cases = random.randint(0, 20)
        
        return cases
    
    def calculate_risk_level(self, cases, population):
        """根據病例數和人口計算風險等級"""
        if population == 0:
            return "低風險"
        
        rate = cases / population * 10000
        
        if rate >= 10:
            return "極高風險"
        elif rate >= 5:
            return "高風險"
        elif rate >= 2:
            return "中風險"
        else:
            return "低風險"
    
    def generate_district_data(self):
        """生成所有行政區的數據"""
        district_data = []
        
        for i, district in enumerate(self.tainan_districts):
            population = self.population_base.get(district, 50000)
            cases = self.generate_dengue_cases(district)
            risk_level = self.calculate_risk_level(cases, population)
            
            update_time = datetime.now() - timedelta(days=random.randint(0, 7))
            
            district_info = {
                "id": i + 1,
                "name": district,
                "population": population,
                "dengue_cases": cases,
                "risk_level": risk_level,
                "last_update": update_time.strftime("%Y-%m-%d %H:%M"),
                "value": cases,
                "rate_per_10k": round(cases / population * 10000, 2) if population > 0 else 0
            }
            
            district_data.append(district_info)
        
        district_data.sort(key=lambda x: x['dengue_cases'], reverse=True)
        
        return district_data
    
    def generate_weather_data(self):
        """生成天氣相關數據"""
        weather_data = {
            "temperature": round(random.uniform(25, 35), 1),
            "humidity": random.randint(60, 90),
            "rainfall": round(random.uniform(0, 50), 1),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return weather_data
    
    def generate_ovitrap_data(self):
        """生成誘卵器數據"""
        ovitrap_data = []
        
        for district in self.tainan_districts:
            num_ovitraps = random.randint(5, 15)
            
            for i in range(num_ovitraps):
                ovitrap_info = {
                    "district": district,
                    "ovitrap_id": f"{district}_{i+1:03d}",
                    "egg_count": random.randint(0, 200),
                    "location": {
                        "lat": round(23.0 + random.uniform(-0.5, 0.5), 6),
                        "lng": round(120.2 + random.uniform(-0.5, 0.5), 6)
                    },
                    "status": random.choice(["正常", "需更換", "故障"]),
                    "last_check": (datetime.now() - timedelta(days=random.randint(0, 14))).strftime("%Y-%m-%d")
                }
                ovitrap_data.append(ovitrap_info)
        
        return ovitrap_data
    
    def save_data_to_json(self, data, filename):
        """保存數據到JSON文件"""
        output_path = os.path.join(os.path.dirname(__file__), 'data', filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"數據已保存到: {output_path}")
        return output_path
    
    def generate_all_data(self):
        """生成所有類型的數據"""
        print("正在生成台南市登革熱疫情模擬數據...")
        
        district_data = self.generate_district_data()
        district_file = self.save_data_to_json(district_data, 'district_data.json')
        
        weather_data = self.generate_weather_data()
        weather_file = self.save_data_to_json(weather_data, 'weather_data.json')
        
        ovitrap_data = self.generate_ovitrap_data()
        ovitrap_file = self.save_data_to_json(ovitrap_data, 'ovitrap_data.json')
        
        combined_data = {
            "districts": district_data,
            "weather": weather_data,
            "ovitraps": ovitrap_data,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_districts": len(district_data),
            "total_cases": sum(d['dengue_cases'] for d in district_data),
            "high_risk_districts": len([d for d in district_data if d['risk_level'] in ['高風險', '極高風險']])
        }
        
        combined_file = self.save_data_to_json(combined_data, 'dengue_data.json')
        
        print("\n=== 數據生成完成 ===")
        print(f"總行政區數: {len(district_data)}")
        print(f"總病例數: {sum(d['dengue_cases'] for d in district_data)}")
        print(f"高風險區域: {len([d for d in district_data if d['risk_level'] in ['高風險', '極高風險']])}")
        print(f"數據文件: {combined_file}")
        
        return combined_data

def main():
    """主函數"""
    generator = DengueDataGenerator()
    data = generator.generate_all_data()
    
    print("\n=== 前5個高風險區域 ===")
    for i, district in enumerate(data['districts'][:5]):
        print(f"{i+1}. {district['name']}: {district['dengue_cases']}例 ({district['risk_level']})")

if __name__ == "__main__":
    main()
