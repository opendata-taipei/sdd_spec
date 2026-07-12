# AI Tool Adapters

`adapters/` 是薄層，不是正式規格來源。其用途是把不同 AI／IDE／CLI 的操作方式映射到相同 SDD Core。

每個 Adapter 應做到：

1. 指示工具先讀取 Constitution、Living Specs、Change 與 State。
2. 將工具輸出寫回標準文件與 JSON State。
3. 不建立只有該工具能理解的 Requirement 或 Gate。
4. 不把聊天記憶、私有 Knowledge Base 或某模型特有能力設為必要條件。
5. 切換工具時，只替換 Adapter，不修改權威規格。

本套件提供 Generic Adapter 範本；實際導入特定供應商前，應依公司核准版本與最新官方文件調整。
