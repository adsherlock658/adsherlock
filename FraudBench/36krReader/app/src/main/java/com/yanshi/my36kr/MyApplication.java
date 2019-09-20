package com.yanshi.my36kr;

import android.app.Application;
import android.graphics.Bitmap;

import com.android.volley.RequestQueue;
import com.android.volley.toolbox.Volley;
import com.facebook.stetho.Stetho;
import com.facebook.stetho.okhttp.StethoInterceptor;
import com.nostra13.universalimageloader.cache.memory.impl.LruMemoryCache;
import com.nostra13.universalimageloader.core.DisplayImageOptions;
import com.nostra13.universalimageloader.core.ImageLoader;
import com.nostra13.universalimageloader.core.ImageLoaderConfiguration;
import com.nostra13.universalimageloader.core.assist.ImageScaleType;
import com.nostra13.universalimageloader.core.display.FadeInBitmapDisplayer;
import com.nostra13.universalimageloader.core.display.RoundedBitmapDisplayer;
import com.squareup.okhttp.OkHttpClient;
import com.yanshi.my36kr.fragment.OkHttpStack;


/**
 * Created by kingars on 2014/10/26.
 */
public class MyApplication extends Application {

    private static MyApplication myApplication;
    private static RequestQueue requestQueue;

    public static MyApplication getInstance() {
        return myApplication;
    }

    public static RequestQueue getRequestQueue() {
        return requestQueue;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        //fb stetho
        Stetho.initialize(
                Stetho.newInitializerBuilder(this)
                        .enableDumpapp(Stetho.defaultDumperPluginsProvider(this))
                        .enableWebKitInspector(Stetho.defaultInspectorModulesProvider(this))
                        .build());


        //由于Application类本身已经单例，所以直接按以下处理即可。
        OkHttpClient client = new OkHttpClient();
        client.networkInterceptors().add(new StethoInterceptor());


        myApplication = this;
        requestQueue = Volley.newRequestQueue(getApplicationContext(), new OkHttpStack(client));
        initImageLoader();
    }

    private void initImageLoader() {
        ImageLoaderConfiguration config = new ImageLoaderConfiguration.Builder(getApplicationContext())
                .memoryCache(new LruMemoryCache(2 * 1024 * 1024))
                .memoryCacheSize(2 * 1024 * 1024)
                .diskCacheSize(30 * 1024 * 1024)
                .diskCacheFileCount(100)
                .build();
        ImageLoader.getInstance().init(config);
    }

    //默认的
    public DisplayImageOptions getOptions() {
        return new DisplayImageOptions.Builder()
                .showImageOnLoading(R.drawable.ic_app_logo)
                .showImageForEmptyUri(R.drawable.ic_app_logo)
                .showImageOnFail(R.drawable.ic_app_logo)
                .cacheInMemory(true)
                .cacheOnDisk(true)
                .imageScaleType(ImageScaleType.IN_SAMPLE_POWER_OF_2) // default
                .bitmapConfig(Bitmap.Config.RGB_565) // default
                .displayer(new FadeInBitmapDisplayer(300))
                .build();
    }

    //自定义默认图的
    public DisplayImageOptions getOptions(int defaultImgResourceId) {
        return new DisplayImageOptions.Builder()
                .showImageOnLoading(defaultImgResourceId)
                .showImageForEmptyUri(defaultImgResourceId)
                .showImageOnFail(defaultImgResourceId)
                .cacheInMemory(true)
                .cacheOnDisk(true)
                .imageScaleType(ImageScaleType.IN_SAMPLE_POWER_OF_2) // default
                .bitmapConfig(Bitmap.Config.RGB_565) // default
                .displayer(new FadeInBitmapDisplayer(300))
                .build();
    }

    //圆角图片
    public DisplayImageOptions getOptionsWithRoundedCorner() {
        return new DisplayImageOptions.Builder()
                .showImageOnLoading(R.drawable.ic_app_logo)
                .showImageForEmptyUri(R.drawable.ic_app_logo)
                .showImageOnFail(R.drawable.ic_app_logo)
                .cacheInMemory(true)
                .cacheOnDisk(true)
                .imageScaleType(ImageScaleType.IN_SAMPLE_POWER_OF_2) // default
                .bitmapConfig(Bitmap.Config.RGB_565) // default
                .displayer(new FadeInBitmapDisplayer(300))
                .displayer(new RoundedBitmapDisplayer(8))
                .build();
    }

}
