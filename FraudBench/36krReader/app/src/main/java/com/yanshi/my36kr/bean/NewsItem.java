package com.yanshi.my36kr.bean;

import com.j256.ormlite.field.DatabaseField;
import com.j256.ormlite.table.DatabaseTable;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.Serializable;

import cn.bmob.v3.BmobObject;

/**
 * 新闻实体类
 * 作者：yanshi
 * 时间：2014-10-24 15:22
 */
@DatabaseTable(tableName = "tb_news_item")
public class NewsItem extends BmobObject implements Serializable {

    @DatabaseField(generatedId = true)
    private int id;
    @DatabaseField(columnName = "title")
    private String title;
    @DatabaseField(columnName = "url")
    private String url;
    @DatabaseField(columnName = "imgUrl")
    private String imgUrl;
    @DatabaseField(columnName = "content")
    private String content;
    @DatabaseField(columnName = "date")
    private String date;
    @DatabaseField(columnName = "newsType")
    private String newsType;
    private String userId;
    @DatabaseField(columnName = "bmobId")
    private String bmobId;//用来删除Bmob数据库中数据时需要

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getImgUrl() {
        return imgUrl;
    }

    public void setImgUrl(String imgUrl) {
        this.imgUrl = imgUrl;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getDate() {
        return date;
    }

    public void setDate(String date) {
        this.date = date;
    }

    public String getNewsType() {
        return newsType;
    }

    public void setNewsType(String newsType) {
        this.newsType = newsType;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getBmobId() {
        return bmobId;
    }

    public void setBmobId(String bmobId) {
        this.bmobId = bmobId;
    }

    public JSONObject toJSONObj() {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("id", id);
            jsonObject.put("title", title);
            jsonObject.put("url", url);
            jsonObject.put("imgUrl", imgUrl);
            jsonObject.put("content", content);
            jsonObject.put("date", date);
            jsonObject.put("newsType", newsType);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jsonObject;
    }

    public static NewsItem parse(JSONObject jsonObject) {
        if (jsonObject == null) {
            return null;
        }
        NewsItem newsItem = new NewsItem();
        newsItem.setId(jsonObject.optInt("id"));
        newsItem.setTitle(jsonObject.optString("title"));
        newsItem.setUrl(jsonObject.optString("url"));
        newsItem.setImgUrl(jsonObject.optString("imgUrl"));
        newsItem.setContent(jsonObject.optString("content"));
        newsItem.setDate(jsonObject.optString("date"));
        newsItem.setNewsType(jsonObject.optString("newsType"));
        return newsItem;
    }

}
