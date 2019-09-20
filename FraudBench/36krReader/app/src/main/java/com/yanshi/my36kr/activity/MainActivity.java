package com.yanshi.my36kr.activity;


import android.content.Intent;
import android.os.Bundle;
import android.os.SystemClock;
import android.support.design.widget.NavigationView;
import android.support.v4.app.ActivityCompat;
import android.support.v4.app.ActivityOptionsCompat;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentTransaction;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBar;
import android.support.v7.widget.Toolbar;
import android.text.TextUtils;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.nostra13.universalimageloader.core.ImageLoader;
import com.yanshi.my36kr.R;
import com.yanshi.my36kr.activity.base.BaseActivity;
import com.yanshi.my36kr.bean.Constant;
import com.yanshi.my36kr.bean.bmob.User;
import com.yanshi.my36kr.biz.UserProxy;
import com.yanshi.my36kr.common.utils.ScreenUtils;
import com.yanshi.my36kr.common.utils.ToastUtils;
import com.yanshi.my36kr.fragment.IndexFragment;
import com.yanshi.my36kr.fragment.NextFragment;
import com.yanshi.my36kr.fragment.SettingsFragment;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdView;

public class MainActivity extends BaseActivity {

    private Toolbar mToolbar;
    private DrawerLayout mDrawerLayout;
    private NavigationView mNavigationView;
    private ImageView userAvatarIv;
    private TextView userNameTv;

    private int[] userAvatars = {R.drawable.ic_avatar_bear, R.drawable.ic_avatar_cat, R.drawable.ic_avatar_monkey,
            R.drawable.ic_avatar_panda, R.drawable.ic_avatar_pig, R.drawable.ic_avatar_raccoon, R.drawable.ic_avatar_rhino};
    private String[] drawerTitles = {"36氪", "NEXT", "设置"};
    private List<Fragment> fragmentList;
    private Class[] classes = {IndexFragment.class, NextFragment.class, SettingsFragment.class};

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);


        fragmentList = new ArrayList<>();
        for (int i = 0; i < 4; i++) {
            fragmentList.add(null);
        }

        findViews();
        selectItem(0);//默认选中第一个
        setUserUI(UserProxy.getInstance().getCurrentUser(this));
        UserProxy.getInstance().addUserInfoChangedListener(userInfoChangedListener);

    }



    private void selectItem(int position) {
        FragmentTransaction fragmentTransaction = this.getSupportFragmentManager().beginTransaction();
        fragmentTransaction.setTransitionStyle(FragmentTransaction.TRANSIT_FRAGMENT_FADE);
        //先隐藏所有fragment
        for (Fragment fragment : fragmentList) {
            if (null != fragment) fragmentTransaction.hide(fragment);
        }

        Fragment fragment;
        if (null == fragmentList.get(position)) {
            Bundle bundle = new Bundle();
            bundle.putString(Constant.TITLE, drawerTitles[position]);
            fragment = Fragment.instantiate(this, classes[position].getName(), bundle);
            fragmentList.set(position, fragment);
            // 如果Fragment为空，则创建一个并添加到界面上
            fragmentTransaction.add(R.id.main_content_fl, fragment);
        } else {
            // 如果Fragment不为空，则直接将它显示出来
            fragment = fragmentList.get(position);

            fragmentTransaction.show(fragment);
        }
        fragmentTransaction.commit();

        setTitle(drawerTitles[position]);
    }

    private void findViews() {
        mToolbar = (Toolbar) findViewById(R.id.toolbar);
        ((LinearLayout.LayoutParams) mToolbar.getLayoutParams()).setMargins(0, ScreenUtils.getStatusBarHeight(this), 0, 0);
        setSupportActionBar(mToolbar);
        ActionBar ab = getSupportActionBar();
        if (null != ab) {
            ab.setHomeAsUpIndicator(R.drawable.ic_menu);
            ab.setDisplayHomeAsUpEnabled(true);
        }

        mDrawerLayout = (DrawerLayout) findViewById(R.id.main_drawer_layout);
        mNavigationView = (NavigationView) findViewById(R.id._main_navigation_view);

        setupDrawerContent(mNavigationView);
    }

    private void setupDrawerContent(NavigationView mNavigationView) {
        View headerView = LayoutInflater.from(this).inflate(R.layout.view_navigation_header, null);
        userAvatarIv = (ImageView) headerView.findViewById(R.id.navigation_header_view_avatar_iv);
        userAvatarIv.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!UserProxy.getInstance().isLogin(MainActivity.this)) {
                    jumpToActivity(MainActivity.this, LoginActivity.class, null);
                } else {
                    ActivityOptionsCompat compat = ActivityOptionsCompat
                            .makeSceneTransitionAnimation(MainActivity.this, v, getString(R.string.shared_elements_avatar_iv));
                    ActivityCompat.startActivity(MainActivity.this, new Intent(MainActivity.this, PersonalActivity.class), compat.toBundle());
                }
            }
        });
        userNameTv = (TextView) headerView.findViewById(R.id.navigation_header_view_name_tv);

        mNavigationView.addHeaderView(headerView);
        mNavigationView.setNavigationItemSelectedListener(new NavigationView.OnNavigationItemSelectedListener() {
            @Override
            public boolean onNavigationItemSelected(MenuItem menuItem) {
                switch (menuItem.getItemId()) {
                    case R.id.nav_index://首页
                        selectItem(0);
                        menuItem.setChecked(true);
                        break;
                    case R.id.nav_next://NEXT
                        selectItem(1);
                        menuItem.setChecked(true);
                        break;
                    case R.id.nav_settings://设置
                        selectItem(2);
                        menuItem.setChecked(true);
                        break;
                    case R.id.nav_personal://个人信息
                        if (!UserProxy.getInstance().isLogin(MainActivity.this)) {
                            jumpToActivity(MainActivity.this, LoginActivity.class, null);
                        } else {
                            jumpToActivity(MainActivity.this, PersonalActivity.class, null);
                        }
                        break;
                    case R.id.nav_favorite://我的收藏
                        if (!UserProxy.getInstance().isLogin(MainActivity.this)) {
                            jumpToActivity(MainActivity.this, LoginActivity.class, null);
                        } else {
                            jumpToActivity(MainActivity.this, FavoriteActivity.class, null);
                        }
                        break;
                }

                mDrawerLayout.closeDrawers();
                return true;
            }
        });
    }

    private void setUserUI(User user) {
        if (user == null) {
            userAvatarIv.setImageResource(userAvatars[new Random().nextInt(6)]);
            userNameTv.setText("未登录");
        } else {
            userNameTv.setText(!TextUtils.isEmpty(user.getNickname()) ? user.getNickname() : user.getUsername());

            String imgUrl;
            if (null != user.getAvatar() && null != (imgUrl = user.getAvatar().getFileUrl())) {
                ImageLoader.getInstance().displayImage(imgUrl, userAvatarIv, mMyApplication.getOptions(0));
            } else {
                userAvatarIv.setImageResource(userAvatars[new Random().nextInt(6)]);
            }
        }
    }

    private UserProxy.UserInfoChangedListener userInfoChangedListener = new UserProxy.UserInfoChangedListener() {
        @Override
        public void onChanged() {
            setUserUI(UserProxy.getInstance().getCurrentUser(MainActivity.this));
        }
    };

    @Override
    protected void onDestroy() {
        super.onDestroy();
        UserProxy.getInstance().removeUserInfoChangedListener(userInfoChangedListener);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case android.R.id.home:
                mDrawerLayout.openDrawer(GravityCompat.START);
                return true;
        }
        return super.onOptionsItemSelected(item);
    }

    private long lastMillis;

    @Override
    public void onBackPressed() {
        if ((System.currentTimeMillis() - lastMillis) > 2000) {
            ToastUtils.show(this, getResources().getString(R.string.quit_tip));
            lastMillis = System.currentTimeMillis();
        } else {
            finish();
        }
    }

    void printSamples(MotionEvent ev) {
        final int historySize = ev.getHistorySize();
        final int pointerCount = ev.getPointerCount();
        long timecurrentTimeMillis;
        long upcurrentTimeMillis;
        long interval;
        long eventTime;
        Log.d("MainActivity", "**************************MotionEvent*************************");
        Log.d("MainActivity", "In printSamples historySize:"+historySize );
        Log.d("MainActivity", "In printSamples pointerCount:"+pointerCount );
        timecurrentTimeMillis = System.currentTimeMillis();
        upcurrentTimeMillis = SystemClock.uptimeMillis();
        interval = timecurrentTimeMillis - upcurrentTimeMillis;

        for (int h = 0; h < historySize; h++) {
            eventTime = ev.getHistoricalEventTime(h) + interval;
            //System.out.printf("Time:", ev.getHistoricalEventTime(h));
            //Log.d("MainActivity", "Time:" + ev.getHistoricalEventTime(h) );
            Log.d("MainActivity", "Time:" + eventTime);

            for (int p = 0; p < pointerCount; p++) {
                Log.d("MainActivity", "PointerID: "+ev.getPointerId(p)+":"+ev.getHistoricalX(p, h)+","+ev.getHistoricalY(p, h));
                Log.d("MainActivity", "Pressure: "+ev.getPressure(p));
                Log.d("MainActivity", "Size: "+ev.getSize(p));
                Log.d("MainActivity", "Source: "+ev.getSource());

                Log.d("MainActivity", "ToolType: "+ev.getToolType(p));
                Log.d("MainActivity", "ToolMajor: "+ev.getToolMajor(p));
                Log.d("MainActivity", "ToolMinor: "+ev.getToolMinor(p));
                Log.d("MainActivity", "Device: "+ev.getDevice());
                Log.d("MainActivity", "DeviceID: "+ev.getDeviceId());
            }
        }
        //System.out.printf("Time: ", ev.getEventTime());
        //Log.d("MainActivity", "Time: " + ev.getEventTime());
        eventTime = ev.getEventTime() + interval;
        Log.d("MainActivity", "Time: " + eventTime);
        for (int p = 0; p < pointerCount; p++) {
            Log.d("MainActivity", "PointerID: " + ev.getPointerId(p) + ":" + ev.getX(p) + "," + ev.getY(p));
            Log.d("MainActivity", "Pressure: " + ev.getPressure(p));
            Log.d("MainActivity", "Size: " + ev.getSize(p));
            Log.d("MainActivity", "Source: " + ev.getSource());

            Log.d("MainActivity", "ToolType: " + ev.getToolType(p));
            Log.d("MainActivity", "ToolMajor: " + ev.getToolMajor(p));
            Log.d("MainActivity", "ToolMinor: " + ev.getToolMinor(p));
            Log.d("MainActivity", "Device: " + ev.getDevice());
            Log.d("MainActivity", "DeviceID: " + ev.getDeviceId());
        }
    }

    @Override
    public boolean dispatchTouchEvent(MotionEvent ev) {

        Log.d("MainActivity", "MainActivity dispatchTouchEvent: " + ev.getAction());
        printSamples(ev);
        return super.dispatchTouchEvent(ev);

        // return value depends on the child.dispatchTouchEvent's return value
        // or if thats false then then this.onTouchEvent's return value
        //boolean bool = super.dispatchTouchEvent(ev);
        //Log.d(TAG, String.valueOf(bool));

        // return false;

    }


    @Override
    public boolean onTouchEvent(MotionEvent ev) {
        Log.d("MainActivity", "MainActivity ontouchevent custom implementation: " + ev.getAction());

        Thread.dumpStack();

        return super.onTouchEvent(ev);
        //return false;
    }

}
