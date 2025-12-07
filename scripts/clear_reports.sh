#!/bin/bash
# 一键清空报告目录下的所有文件

BASE_DIR="/home/dzs-ai-4/dzs-dev/Agent/multiRunningAgents"

rm -rf "$BASE_DIR/query_engine_streamlit_reports"/*
rm -rf "$BASE_DIR/media_engine_streamlit_reports"/*
rm -rf "$BASE_DIR/insight_engine_streamlit_reports"/*
rm -rf "$BASE_DIR/final_reports"/*

echo "报告目录已清空"
