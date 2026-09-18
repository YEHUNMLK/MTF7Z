<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="zh_CN">
<context>
    <name>Archive</name>
    <message>
        <location filename="../main.py" line="82"/>
        <source>Unable to read the 7z archive</source>
        <translation>无法读取 7z 压缩包</translation>
    </message>
    <message>
        <location filename="../main.py" line="131"/>
        <source>Failed to extract: {archive_name}</source>
        <translation>解压失败：{archive_name}</translation>
    </message>
    <message>
        <location filename="../main.py" line="135"/>
        <source>7-Zip did not output the expected file: {archive_name}</source>
        <translation>7-Zip 未输出预期的文件：{archive_name}</translation>
    </message>
    <message>
        <location filename="../main.py" line="146"/>
        <source>7-Zip Operation Failed</source>
        <translation>7-Zip 操作失败</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../main.py" line="227"/>
        <source>File / Directory</source>
        <translation>文件/目录</translation>
    </message>
    <message>
        <location filename="../main.py" line="227"/>
        <source>Status</source>
        <translation>状态</translation>
    </message>
    <message>
        <location filename="../main.py" line="271"/>
        <source>Open 7z</source>
        <translation>打开 7z</translation>
    </message>
    <message>
        <location filename="../main.py" line="273"/>
        <source>Open a 7z archive.</source>
        <translation>打开一个 7z 压缩包。</translation>
    </message>
    <message>
        <location filename="../main.py" line="277"/>
        <source>Edit</source>
        <translation>编辑</translation>
    </message>
    <message>
        <location filename="../main.py" line="280"/>
        <source>Open and edit selected files.</source>
        <translation>打开并编辑选中的文件。</translation>
    </message>
    <message>
        <location filename="../main.py" line="284"/>
        <source>Update</source>
        <translation>更新</translation>
    </message>
    <message>
        <location filename="../main.py" line="287"/>
        <source>Apply changes to the 7z archive.</source>
        <translation>将更改应用到 7z 压缩包。</translation>
    </message>
    <message>
        <location filename="../main.py" line="291"/>
        <source>Extract</source>
        <translation>解压</translation>
    </message>
    <message>
        <location filename="../main.py" line="295"/>
        <source>Extract selected files to the temporary directory.</source>
        <translation>将选中的文件解压到临时目录。</translation>
    </message>
    <message>
        <location filename="../main.py" line="299"/>
        <source>Compression Level:</source>
        <translation>压缩等级：</translation>
    </message>
    <message>
        <location filename="../main.py" line="303"/>
        <source>Compression level used when updating/adding files to the 7-Zip archive. 0 means store only.</source>
        <translation>更新/添加文件到 7-Zip 压缩包时使用的压缩等级。0 表示仅存储不压缩。</translation>
    </message>
    <message>
        <location filename="../main.py" line="307"/>
        <source>Refresh</source>
        <translation>刷新</translation>
    </message>
    <message>
        <location filename="../main.py" line="309"/>
        <source>Refresh to check for changes.</source>
        <translation>刷新以检查更改。</translation>
    </message>
    <message>
        <location filename="../main.py" line="313"/>
        <source>Close 7z</source>
        <translation>关闭 7z</translation>
    </message>
    <message>
        <location filename="../main.py" line="315"/>
        <source>Close the open 7z archive.</source>
        <translation>关闭当前打开的 7z 压缩包。</translation>
    </message>
    <message>
        <location filename="../main.py" line="320"/>
        <location filename="../main.py" line="373"/>
        <source>Language</source>
        <translation>语言</translation>
    </message>
    <message>
        <location filename="../main.py" line="374"/>
        <source>The language will take effect after restarting the program.</source>
        <translation>语言设置将在重启程序后生效。</translation>
    </message>
    <message>
        <location filename="../main.py" line="384"/>
        <source>Open 7z File</source>
        <translation>打开 7z 文件</translation>
    </message>
    <message>
        <location filename="../main.py" line="391"/>
        <source>7-Zip Not Found</source>
        <translation>未找到 7-Zip</translation>
    </message>
    <message>
        <location filename="../main.py" line="392"/>
        <source>The 7z/7zz command was not found.
Please install 7-Zip first.</source>
        <translation>未找到 7z/7zz 命令。
请先安装 7-Zip。</translation>
    </message>
    <message>
        <location filename="../main.py" line="413"/>
        <source>Open Failed</source>
        <translation>打开失败</translation>
    </message>
    <message>
        <location filename="../main.py" line="493"/>
        <location filename="../main.py" line="723"/>
        <location filename="../main.py" line="738"/>
        <location filename="../main.py" line="761"/>
        <source>Extracted</source>
        <translation>已解压</translation>
    </message>
    <message>
        <location filename="../main.py" line="519"/>
        <source>Extracted: {archive_name}</source>
        <translation>已解压：{archive_name}</translation>
    </message>
    <message>
        <location filename="../main.py" line="521"/>
        <source>Extraction Failed</source>
        <translation>解压失败</translation>
    </message>
    <message>
        <source>Edited</source>
        <translation type="vanished">已编辑</translation>
    </message>
    <message>
        <location filename="../main.py" line="537"/>
        <source>No external editor was found for this file type. Extracted only: {archive_name}</source>
        <translation>未找到适用于该文件类型的外部编辑器，仅已解压：{archive_name}</translation>
    </message>
    <message>
        <location filename="../main.py" line="547"/>
        <source>Edit/Extraction Failed</source>
        <translation>编辑/解压失败</translation>
    </message>
    <message>
        <location filename="../main.py" line="556"/>
        <source>Unable to open external editor</source>
        <translation>无法打开外部编辑器</translation>
    </message>
    <message>
        <location filename="../main.py" line="558"/>
        <source>File was extracted to:
{path}

but xdg-open could not be invoked:
{e}</source>
        <translation>文件已解压到：
{path}

但无法调用 xdg-open：
{e}</translation>
    </message>
    <message>
        <location filename="../main.py" line="582"/>
        <source>Temporary File Deleted</source>
        <translation>临时文件已删除</translation>
    </message>
    <message>
        <location filename="../main.py" line="584"/>
        <source>Modified, Pending Update</source>
        <translation>已修改，待更新</translation>
    </message>
    <message>
        <location filename="../main.py" line="668"/>
        <source>Extracted/edited {counts_edited} file(s).  Found {counts_changes} changes in the temporary directory.</source>
        <translation>已解压/编辑 {counts_edited} 个文件。在临时目录中发现 {counts_changes} 处更改。</translation>
    </message>
    <message>
        <location filename="../main.py" line="682"/>
        <source>Temporary File Not Found</source>
        <translation>未找到临时文件</translation>
    </message>
    <message>
        <location filename="../main.py" line="684"/>
        <source>The file in the temporary directory has been deleted:
{name}

Delete the corresponding file from the 7z archive as well?</source>
        <translation>临时目录中的文件已被删除：
{name}

是否同时从 7z 压缩包中删除对应的文件？</translation>
    </message>
    <message>
        <location filename="../main.py" line="698"/>
        <source>Deletion Failed</source>
        <translation>删除失败</translation>
    </message>
    <message>
        <location filename="../main.py" line="698"/>
        <source>Failed to delete {name}:

{e}</source>
        <translation>删除 {name} 失败：

{e}</translation>
    </message>
    <message>
        <location filename="../main.py" line="705"/>
        <source>File</source>
        <translation>文件</translation>
    </message>
    <message>
        <location filename="../main.py" line="705"/>
        <source>Directory</source>
        <translation>目录</translation>
    </message>
    <message>
        <location filename="../main.py" line="707"/>
        <source>New {_type} Found</source>
        <translation>发现新{_type}</translation>
    </message>
    <message>
        <location filename="../main.py" line="709"/>
        <source>A new {_type} not present in the 7z archive was found in the temporary directory:
{name}

Add it to the 7z archive?</source>
        <translation>在临时目录中发现一个 7z 压缩包中不存在的新{_type}：
{name}

是否将其添加到 7z 压缩包？</translation>
    </message>
    <message>
        <location filename="../main.py" line="741"/>
        <source>Add Failed</source>
        <translation>添加失败</translation>
    </message>
    <message>
        <location filename="../main.py" line="741"/>
        <source>Failed to add {name}:

{e}</source>
        <translation>添加 {name} 失败：

{e}</translation>
    </message>
    <message>
        <location filename="../main.py" line="749"/>
        <source>File Modified</source>
        <translation>文件已修改</translation>
    </message>
    <message>
        <location filename="../main.py" line="750"/>
        <source>File:
{name}

The temporary file has been modified.
Update the 7z archive?</source>
        <translation>文件：
{name}

临时文件已被修改。
是否更新 7z 压缩包？</translation>
    </message>
    <message>
        <location filename="../main.py" line="763"/>
        <source>Update Failed</source>
        <translation>更新失败</translation>
    </message>
    <message>
        <location filename="../main.py" line="763"/>
        <source>Failed to update {name}:

{e}</source>
        <translation>更新 {name} 失败：

{e}</translation>
    </message>
    <message>
        <location filename="../main.py" line="828"/>
        <source>Unprocessed Changes Remain</source>
        <translation>仍有未处理的更改</translation>
    </message>
    <message>
        <location filename="../main.py" line="830"/>
        <source>The following items have not yet been updated to the 7z archive:

{names}

The temporary directory will be deleted when the archive is closed, and these changes will be lost. Continue closing?</source>
        <translation>以下项目尚未更新到 7z 压缩包：

{names}

关闭压缩包时将删除临时目录，这些更改将会丢失。是否继续关闭？</translation>
    </message>
    <message>
        <location filename="../main.py" line="842"/>
        <source>Cleanup Failed</source>
        <translation>清理失败</translation>
    </message>
    <message>
        <location filename="../main.py" line="844"/>
        <source>Unable to delete the temporary directory:
{_path}

{e}

To prevent loss of changes, this 7z archive will remain open.</source>
        <translation>无法删除临时目录：
{_path}

{e}

为防止更改丢失，此 7z 压缩包将保持打开状态。</translation>
    </message>
    <message>
        <location filename="../main.py" line="859"/>
        <source>No 7z Archive Open</source>
        <translation>没有打开的 7z 压缩包</translation>
    </message>
</context>
<context>
    <name>Startup</name>
    <message>
        <location filename="../main.py" line="883"/>
        <source>Failed to load translation.</source>
        <translation>加载翻译失败。</translation>
    </message>
    <message>
        <location filename="../main.py" line="897"/>
        <source>7z/7zz was not found at startup.
Install 7-Zip to use this feature.</source>
        <translation>启动时未找到 7z/7zz。
请安装 7-Zip 以使用此功能。</translation>
    </message>
</context>
</TS>
