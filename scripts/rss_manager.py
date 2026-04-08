import os
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

class RSSManager:
    """RSS存储管理类"""
    
    def __init__(self):
        """初始化RSS管理器"""
        # RSS存储文件路径
        self.rss_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "rss.xml")
        # 最大保留条目数
        self.max_entries = 50
        # 输出初始化信息
        print(f"📁 RSS文件路径：{self.rss_file}")
        print(f"📁 目录是否存在：{os.path.exists(os.path.dirname(self.rss_file))}")
        print(f"📄 文件是否存在：{os.path.exists(self.rss_file)}")
    
    def _ensure_file_exists(self):
        """确保RSS文件存在"""
        # 确保目录存在
        dir_path = os.path.dirname(self.rss_file)
        if not os.path.exists(dir_path):
            print(f"📁 目录不存在，创建目录：{dir_path}")
            os.makedirs(dir_path, exist_ok=True)
        
        if not os.path.exists(self.rss_file):
            print(f"📄 文件不存在，创建初始文件：{self.rss_file}")
            # 创建标准的RSS 2.0 XML结构
            rss = ET.Element('rss')
            rss.set('version', '2.0')
            channel = ET.SubElement(rss, 'channel')
            title = ET.SubElement(channel, 'title')
            title.text = 'RSS汇总'
            link = ET.SubElement(channel, 'link')
            link.text = 'https://example.com'
            description = ET.SubElement(channel, 'description')
            description.text = '多个RSS源的汇总'
            lastBuildDate = ET.SubElement(channel, 'lastBuildDate')
            lastBuildDate.text = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # 写入文件
            tree = ET.ElementTree(rss)
            with open(self.rss_file, 'wb') as f:
                tree.write(f, encoding='utf-8', xml_declaration=True)
            print(f"✅ 初始文件创建成功")
        else:
            print(f"✅ 文件已存在：{self.rss_file}")
    
    def _reset_stats_if_needed(self, data):
        """检查并重置统计信息（每天0点）"""
        # 获取当前北京时间日期
        current_date = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d')
        
        # 检查缓存中的统计日期
        stats_date = data.get('stats_date')
        
        # 如果日期不同，重置统计信息
        if stats_date != current_date:
            print(f"📅 日期变更，重置统计信息（{stats_date} → {current_date}")
            data['stats_date'] = current_date
            data['stats'] = []
        
        return data
    
    def read_rss_data(self):
        """读取RSS数据
        
        Returns:
            dict: RSS数据，包含 last_update_time、rss 和 stats 字段
        """
        self._ensure_file_exists()
        
        try:
            # 解析XML文件
            tree = ET.parse(self.rss_file)
            root = tree.getroot()
            channel = root.find('channel')
            
            # 提取RSS条目
            rss_items = []
            for item in channel.findall('item'):
                rss_item = {
                    "guid": item.findtext('guid', ''),
                    "link": item.findtext('link', ''),
                    "published": item.findtext('pubDate', ''),
                    "source_name": item.findtext('source', ''),
                    "summary": item.findtext('description', ''),
                    "title": item.findtext('title', '')
                }
                rss_items.append(rss_item)
            
            # 提取lastBuildDate
            last_update_time = channel.findtext('lastBuildDate', '')
            
            # 构建返回数据
            data = {
                "last_update_time": last_update_time,
                "rss": rss_items,
                "stats": [],
                "stats_date": datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d')
            }
            
            # 检查并重置统计信息
            data = self._reset_stats_if_needed(data)
            
            print(f"✅ RSS数据读取成功，上次更新时间：{data.get('last_update_time', '无')}")
            print(f"📊 当前统计日期：{data.get('stats_date', '无')}")
            print(f"📋 存储的RSS条目数：{len(data.get('rss', []))}")
            print(f"📈 统计信息条数：{len(data.get('stats', []))}")
        except Exception as e:
            print(f"⚠️ RSS文件读取错误：{str(e)}，已重置数据")
            # 创建初始结构
            data = {
                "last_update_time": None,
                "rss": [],
                "stats": [],
                "stats_date": datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d')
            }
            # 重新创建XML文件
            self._ensure_file_exists()
        
        return data
    
    def update_rss_data(self, entries, source_stats):
        """更新RSS数据
        
        Args:
            entries (list): 新的RSS条目列表
            source_stats (dict): 源站统计信息
        """
        # 读取现有数据
        data = self.read_rss_data()
        
        # 获取当前北京时间
        current_time = datetime.now(ZoneInfo('Asia/Shanghai'))
        current_date = current_time.strftime('%Y-%m-%d')
        # 标准RSS时间格式：Wed, 02 Oct 2002 08:00:00 EST
        rss_time_format = current_time.strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # 合并并去重RSS条目
        existing_guids = set()
        for item in data['rss']:
            guid = item.get('guid')
            if guid:
                existing_guids.add(guid)
            else:
                # 使用link作为备选唯一标识符
                link = item.get('link')
                if link:
                    existing_guids.add(link)
        
        new_entries = []
        
        for entry in entries:
            # 优先使用guid作为唯一标识符
            guid = entry.get('guid')
            if not guid:
                # 如果没有guid，使用link作为备选
                guid = entry.get('link')
            
            if guid and guid not in existing_guids:
                # 处理时间格式
                published = entry.get('published', '')
                rss_published = ''
                if published:
                    from dateutil.parser import parse
                    try:
                        dt = parse(published)
                        # 转换为标准RSS时间格式
                        rss_published = dt.strftime('%a, %d %b %Y %H:%M:%S %z')
                    except:
                        pass
                
                # 确保条目标结构完整
                rss_item = {
                    "guid": guid,
                    "link": entry.get('link', ''),
                    "published": rss_published,
                    "source_name": entry.get('source_name', ''),
                    "summary": entry.get('summary', entry.get('description', '')),
                    "title": entry.get('title', '')
                }
                new_entries.append(rss_item)
                existing_guids.add(guid)
        
        # 合并所有条目
        all_entries = new_entries + data['rss']
        
        # 统一处理时间格式
        for entry in all_entries:
            published = entry.get('published', '')
            if published:
                from dateutil.parser import parse
                try:
                    dt = parse(published)
                    # 转换为标准RSS时间格式
                    entry['published'] = dt.strftime('%a, %d %b %Y %H:%M:%S %z')
                except:
                    pass
        
        # 按发布时间排序（降序）
        def get_entry_timestamp(entry):
            """获取条目的时间戳"""
            from dateutil.parser import parse
            try:
                pub_date = entry.get('published', '')
                if pub_date:
                    dt = parse(pub_date)
                    return dt.timestamp()
            except:
                pass
            return 0
        
        all_entries.sort(key=get_entry_timestamp, reverse=True)
        
        # 限制条目数量
        all_entries = all_entries[:self.max_entries]
        
        # 更新统计信息
        # 检查当前日期是否与存储的统计日期相同
        if data.get('stats_date') == current_date:
            # 当天的统计信息需要累加
            existing_stats = {}
            for stat in data.get('stats', []):
                existing_stats[stat['source']] = {
                    'success': stat.get('success', 0),
                    'failed': stat.get('failed', 0)
                }
            
            # 累加统计信息
            for source_name, stat in source_stats.items():
                if source_name in existing_stats:
                    existing_stats[source_name]['success'] += stat.get('success', 0)
                    existing_stats[source_name]['failed'] += stat.get('failure', 0)
                else:
                    existing_stats[source_name] = {
                        'success': stat.get('success', 0),
                        'failed': stat.get('failure', 0)
                    }
            
            # 转换为列表格式
            stats = []
            for source_name, stat in existing_stats.items():
                stats.append({
                    "source": source_name,
                    "success": stat['success'],
                    "failed": stat['failed']
                })
        else:
            # 新的一天，重置统计信息
            stats = []
            for source_name, stat in source_stats.items():
                stats.append({
                    "source": source_name,
                    "success": stat.get('success', 0),
                    "failed": stat.get('failure', 0)
                })
        
        # 生成标准的RSS 2.0 XML结构
        rss = ET.Element('rss')
        rss.set('version', '2.0')
        channel = ET.SubElement(rss, 'channel')
        
        # 频道信息
        title = ET.SubElement(channel, 'title')
        title.text = 'RSS汇总'
        link = ET.SubElement(channel, 'link')
        link.text = 'https://example.com'
        description = ET.SubElement(channel, 'description')
        description.text = '多个RSS源的汇总'
        lastBuildDate = ET.SubElement(channel, 'lastBuildDate')
        lastBuildDate.text = rss_time_format
        language = ET.SubElement(channel, 'language')
        language.text = 'zh-CN'
        
        # 添加RSS条目
        for entry in all_entries:
            item = ET.SubElement(channel, 'item')
            item_title = ET.SubElement(item, 'title')
            item_title.text = entry.get('title', '')
            item_link = ET.SubElement(item, 'link')
            item_link.text = entry.get('link', '')
            item_description = ET.SubElement(item, 'description')
            item_description.text = entry.get('summary', '')
            item_guid = ET.SubElement(item, 'guid')
            item_guid.text = entry.get('guid', '')
            item_guid.set('isPermaLink', 'false')
            item_pubDate = ET.SubElement(item, 'pubDate')
            item_pubDate.text = entry.get('published', '')
            item_source = ET.SubElement(item, 'source')
            item_source.text = entry.get('source_name', '')
        
        # 写入文件
        try:
            print(f"💾 开始写入文件：{self.rss_file}")
            print(f"📋 写入的RSS条目数：{len(all_entries)}")
            print(f"📈 写入的统计信息数：{len(stats)}")
            
            # 美化XML输出
            def indent(elem, level=0):
                i = "\n" + level*"  "
                if len(elem):
                    if not elem.text or not elem.text.strip():
                        elem.text = i + "  "
                    if not elem.tail or not elem.tail.strip():
                        elem.tail = i
                    for elem in elem:
                        indent(elem, level+1)
                    if not elem.tail or not elem.tail.strip():
                        elem.tail = i
                else:
                    if level and (not elem.tail or not elem.tail.strip()):
                        elem.tail = i
            
            indent(rss)
            
            tree = ET.ElementTree(rss)
            with open(self.rss_file, 'wb') as f:
                tree.write(f, encoding='utf-8', xml_declaration=True)
            
            print(f"✅ 文件写入成功")
            print(f"📁 文件大小：{os.path.getsize(self.rss_file)} 字节")
        except Exception as e:
            print(f"❌ 文件写入失败：{str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"💾 RSS数据已更新，上次更新时间：{rss_time_format}")
        print(f"📋 存储的RSS条目数：{len(all_entries)}")
        print(f"📈 统计信息已更新，共{len(stats)}个源站")
    
    def get_last_update_time(self):
        """获取上次更新时间
        
        Returns:
            str: 上次更新时间
        """
        data = self.read_rss_data()
        return data.get('last_update_time')
    
    def get_source_stats(self):
        """获取源站统计信息
        
        Returns:
            dict: 源站统计信息
        """
        data = self.read_rss_data()
        stats = {}
        for stat in data.get('stats', []):
            stats[stat['source']] = {
                'success': stat.get('success', 0),
                'failure': stat.get('failed', 0)
            }
        return stats
